from typing import Any, List

from mapa.core.data.query_args import QueryArgs
from fastapi import Depends, Query
from pydantic import Json, ValidationError, TypeAdapter


def json_param(param_name: str, model: Any, **query_kwargs):
    """Parse JSON-encoded query parameters as pydantic models.
    The function returns a `Depends()` instance that takes the JSON-encoded value from
    the query parameter `param_name` and converts it to a Pydantic model, defined
    by the `model` attribute.
    """

    def get_parsed_object(value: Json = Query(None, alias=param_name, **query_kwargs)):
        try:
            return TypeAdapter(model, value) if value else None
        except ValidationError as err:
            raise err
    return Depends(get_parsed_object)

def query_param(**query_kwargs):
    """Http metodlarında kullanılan query: Json parametresini Json formatında okuyup
    QueryArgs nesnesine dönüştürür. None olması durumunda default QueryArgs döndürülür.
    """
    def inner(query: Json = Query(None, **query_kwargs)):
        return TypeAdapter(QueryArgs).validate_python(query) if query else QueryArgs()
    return Depends(inner)


def fields_param(**query_kwargs):
    """field_list parametresini okur ve liste haline getirir. Parametre None 
    olabilir.
    """
    def inner(field_list: Json = Query(None, **query_kwargs)):
        return TypeAdapter(List).validate_python(field_list) if field_list else None
    return Depends(inner)