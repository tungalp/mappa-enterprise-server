from typing import List

class Util:
    """Sistemde kullanılacak ortak metotları içeren sınıftır."""
    
    #Tarih formatları
    DDMMYYYHHmmssPattern = r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4}) (\d{2}):(\d{2}):(\d{2})$'
    DDMMYYYPattern = r'^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-(\d{4})$'
    dateIsoPattern = r'^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])T([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
    DDMMYYYHHmmssSlashPattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4}) (\d{2}):(\d{2}):(\d{2})$'
    DDMMYYYSlashPattern = r'^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(\d{4})$'
    #Tarih formatları
    
    @staticmethod
    def feature_collection_to_entity(feature_collection, geom_field_name: str):
        """FeatureCollection olarak verilen datayı row halinde geri döner."""
        rowData = []
        for feature in feature_collection["features"]:
            rowData.append(Util.feature_to_entity(feature, geom_field_name))
        return rowData

    @staticmethod
    def features_to_entity(features: List, geom_field_name: str):
        """Feature listesi olarak verilen datayı row halinde geri döner."""
        rowData = []
        for feature in features:
            rowData.append(Util.feature_to_entity(feature, geom_field_name))
        return rowData

    @staticmethod
    def feature_to_entity(feature, geom_field_name: str):
        """Feature olarak verilen datayı row halinde geri döner."""
        geojs = {k: v for k, v in feature["properties"].items()
                 if k != geom_field_name}
        geojs[geom_field_name] = feature['geometry']
        return geojs

    @staticmethod
    def entity_to_feature_collection(data: List, geom_field_name: str):
        """Data'dan FeatureCollection oluşturarak döner."""
        geojs = {
            'type': 'FeatureCollection',
            'features': Util.entity_to_features(data, geom_field_name)
        }
        return geojs

    @staticmethod
    def entity_to_features(data: List, geom_field_name: str):
        """Data'dan Liste Feature oluşturur ve döner."""
        geojs = [
            Util.entity_to_feature(d, geom_field_name) for d in data
        ]
        return geojs

    @staticmethod
    def entity_to_feature(data, geom_field_name: str):
        """Data'dan Feature oluşturarak döner."""
        geom = data[geom_field_name]
        properties = {k: v for k, v in data.items() if k != geom_field_name}
        geojs = {
            'geometry': geom,
            'properties': properties,
            'type': 'Feature'
        }
        return geojs

