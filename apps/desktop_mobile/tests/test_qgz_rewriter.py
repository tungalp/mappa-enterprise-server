import pytest
import zipfile
import io
import xml.etree.ElementTree as ET
from desktop_mobile.shared.utils import process_qgz_project
from desktop_mobile.models.schemas import MapResponse

class MockLayer:
    def __init__(self, url_path, bucket, name=None, layer_type="vector", id=None):
        self.url_path = url_path
        self.bucket = bucket
        self.name = name
        self.type = layer_type
        self.id = id or "test-layer-id"

def test_process_qgz_project_rewrites_datasources():
    # 1. Create a dummy QGS XML content
    qgs_xml = """<qgis projectname="Test Project">
  <projectlayers>
    <maplayer id="layer1" type="vector">
      <layername>rivers</layername>
      <datasource>C:\\Users\\bkryk\\Downloads\\river_networks.GPKG|layername=rivers</datasource>
    </maplayer>
    <maplayer id="layer2" type="vector">
      <layername>roads</layername>
      <datasource>./local_roads.geojson</datasource>
    </maplayer>
    <maplayer id="layer3" type="vector">
      <layername>wms_layer</layername>
      <datasource>http://example.com/wms?SERVICE=WMS</datasource>
    </maplayer>
  </projectlayers>
</qgis>"""

    # 2. Package it into in-memory zip bytes (.qgz)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("project.qgs", qgs_xml.encode("utf-8"))
        zip_file.writestr("some_metadata.txt", b"hello world")
        
    qgz_bytes = zip_buffer.getvalue()

    # 3. Build the layers lookup dictionary
    layers_lookup = {
        "river_networks.gpkg": MockLayer("layers/uuid-1/river_networks.gpkg", "desktop-mobile", "rivers", "gpkg"),
        "local_roads.geojson": MockLayer("layers/uuid-2/local_roads.geojson", "desktop-mobile", "roads", "geojson")
    }

    # 4. Process the QGZ project
    modified_bytes = process_qgz_project(qgz_bytes, layers_lookup)
    assert modified_bytes is not None

    # 5. Extract and parse the modified zip
    modified_buffer = io.BytesIO(modified_bytes)
    with zipfile.ZipFile(modified_buffer, "r") as zip_file:
        assert "project.qgs" in zip_file.namelist()
        assert "some_metadata.txt" in zip_file.namelist()
        
        modified_qgs = zip_file.read("project.qgs").decode("utf-8")
        modified_meta = zip_file.read("some_metadata.txt").decode("utf-8")
        
        assert modified_meta == "hello world"

    # 6. Parse modified XML and assert changes
    root = ET.fromstring(modified_qgs)
    datasources = [ds.text for ds in root.findall(".//datasource")]
    
    assert len(datasources) == 3
    # Check Layer 1 (GPKG rewritten)
    assert datasources[0] == "/vsis3/desktop-mobile/layers/uuid-1/river_networks.gpkg|layername=rivers"
    # Check Layer 2 (GeoJSON rewritten)
    assert datasources[1] == "/vsis3/desktop-mobile/layers/uuid-2/local_roads.geojson"
    # Check Layer 3 (WMS untouched)
    assert datasources[2] == "http://example.com/wms?SERVICE=WMS"

def test_map_response_ogc_urls_generation():
    class DummyMapEntity:
        def __init__(self):
            self.id = "c3f8e5b2-3f8c-4a3d-8b2a-c3f8e5b23f8c"
            self.name = "My Test Map"
            self.description = "Test Description"
            self.project_file_url = "maps/c3f8e5b2-3f8c-4a3d-8b2a-c3f8e5b23f8c/abcd-project.qgz"
            self.creator = "user1"
            self.updater = "user1"
            self.created_at = "2026-05-28T02:08:53"
            self.updated_at = "2026-05-28T02:08:53"
            self.web_map_id = None

    entity = DummyMapEntity()
    response = MapResponse.model_validate(entity)

    assert response.has_project_file is True
    assert response.qgis_server_wms_url is not None
    assert "SERVICE=WMS" in response.qgis_server_wms_url
    assert "MAP=/vsis3/desktop-mobile/maps/" in response.qgis_server_wms_url
    
    assert response.qgis_server_wfs_url is not None
    assert "SERVICE=WFS" in response.qgis_server_wfs_url
    
    assert response.qgis_server_wmts_url is not None
    assert "SERVICE=WMTS" in response.qgis_server_wmts_url

    # Test without project file
    entity.project_file_url = None
    response_no_file = MapResponse.model_validate(entity)
    assert response_no_file.has_project_file is False
    assert response_no_file.qgis_server_wms_url is None
    assert response_no_file.qgis_server_wfs_url is None
    assert response_no_file.qgis_server_wmts_url is None

def test_process_qgz_project_layer_tree_source_and_groups():
    from desktop_mobile.shared.utils import process_qgs_xml, extract_layer_groups

    # 1. Create a dummy QGS XML content with layer-tree hierarchy
    qgs_xml = """<qgis projectname="Test Project">
  <projectlayers>
    <maplayer id="layer1_id" type="vector">
      <layername>rivers</layername>
      <datasource>C:\\Users\\bkryk\\Downloads\\river_networks.GPKG|layername=rivers</datasource>
    </maplayer>
    <maplayer id="layer2_id" type="vector">
      <layername>roads</layername>
      <datasource>./local_roads.geojson</datasource>
    </maplayer>
  </projectlayers>
  <layer-tree-group>
    <layer-tree-group name="main_layers">
      <layer-tree-layer id="layer1_id" source="C:\\Users\\bkryk\\Downloads\\river_networks.GPKG|layername=rivers" name="rivers" providerKey="ogr"/>
    </layer-tree-group>
    <layer-tree-layer id="layer2_id" source="./local_roads.geojson" name="roads" providerKey="ogr"/>
  </layer-tree-group>
</qgis>"""

    layers_lookup = {
        "river_networks.gpkg": MockLayer("layers/uuid-1/river_networks.gpkg", "desktop-mobile", "rivers", "gpkg", "layer1-uuid"),
        "local_roads.geojson": MockLayer("layers/uuid-2/local_roads.geojson", "desktop-mobile", "roads", "geojson", "layer2-uuid")
    }

    # Test processing/rewriting
    modified_xml_bytes = process_qgs_xml(qgs_xml.encode("utf-8"), layers_lookup)
    modified_xml = modified_xml_bytes.decode("utf-8")
    
    root = ET.fromstring(modified_xml)
    
    # Assert datasource elements
    datasources = [ds.text for ds in root.findall(".//datasource")]
    assert datasources[0] == "/vsis3/desktop-mobile/layers/uuid-1/river_networks.gpkg|layername=rivers"
    assert datasources[1] == "/vsis3/desktop-mobile/layers/uuid-2/local_roads.geojson"
    
    # Assert layer-tree-layer source attributes
    layer_tree_sources = [ltl.get("source") for ltl in root.findall(".//layer-tree-layer")]
    assert layer_tree_sources[0] == "/vsis3/desktop-mobile/layers/uuid-1/river_networks.gpkg|layername=rivers"
    assert layer_tree_sources[1] == "/vsis3/desktop-mobile/layers/uuid-2/local_roads.geojson"

    # Test extract_layer_groups
    groups = extract_layer_groups(qgs_xml.encode("utf-8"), layers_lookup)
    assert groups == {
        "layer1-uuid": "main_layers",
        "layer2-uuid": ""
    }
