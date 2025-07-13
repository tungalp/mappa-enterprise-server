import pytest

from mapa.core.data.util import Util
from .data import feature_collection,  feature, features, geo_datas, geo_data


@pytest.mark.asyncio
async def test_data_to_feature():
    """Data'yı Feature'a çeviren test metodu."""
    data = Util.entity_to_feature(geo_data, 'geometry')
    print("Entity2Feature: ", data)
    assert data is not None


@pytest.mark.asyncio
async def test_data_to_features():
    """Data'yı Feature Listesine çeviren test metodu."""
    data = Util.entity_to_features(geo_datas, 'geometry')
    print("Entity2Features: ", data)
    assert data is not None


@pytest.mark.asyncio
async def test_data_to_featurecollection():
    """Data'yı Feature Collectiona'a çeviren test metodu."""
    data = Util.entity_to_feature_collection(geo_datas, 'geometry')
    print("Entity2FeatureCollection: ", data)
    assert data is not None


@pytest.mark.asyncio
async def test_feature_to_data():
    """Feature'ı Data'ya çeviren test metodu."""
    data = Util.feature_to_entity(feature, 'geom')
    print("Feature2Entity: ", data)
    assert data is not None


@pytest.mark.asyncio
async def test_data_features_to_data():
    """Feature Listesini Data Listesine çeviren test metodu."""
    data = Util.features_to_entity(features, 'geom')
    print("Features2Entity: ", data)
    assert data is not None


@pytest.mark.asyncio
async def test_feature_collection_to_data():
    """Feature Collection'u Data Listesine çeviren test metodu."""
    data = Util.feature_collection_to_entity(feature_collection, 'geom')
    print("FeatureCollection2Entity: ", data)
    assert data is not None
