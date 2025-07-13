
from typing import Any, List

from pydantic import BaseModel


class ValidationRule(BaseModel):
    """ValidationRule Model"""
    
    format: str | None = None
    regex: str | None = None
    err_message: str | None = None
    min_length: int | None = None
    max_length: int | None = None
    min_value: int | None = None
    max_value: int | None = None
    no_whitespace: bool | None = None
    required: bool | None = None


class FieldDefinition(BaseModel):
    """FieldDefinition Model"""
    
    enum: Any | None = None

#  destination_layer_id : Hangi katman üzerinden topology işlemin yapılacağı bilgisidir
#  expression : RuleType'ı relate olarak secildiğinde girilmesi gereken bir alandır ve T - F - * parametrelerinden oluşmaktadır. Örn: T*F**FFF*
class FieldParams(BaseModel):
    """FieldParams Model"""

    name: str | None = None
    type: str | None = None
    alias: str | None = None
    attribute_panel: bool | None = None
    listable: bool | None = None
    editable: bool | None = None
    multiple_editable: bool | None = None
    searchable: bool | None = None
    info: bool | None = None
    required: bool | None = None
    length: int | None = None
    definitions: FieldDefinition | None = None
    validation_rules: List[ValidationRule] | None = None
    sortable: bool | None = None
    text_search: bool | None = None
    order: int | None = None
    value_path: str | None = None
    label_prop_name: str | None = None
    value_prop_name: str | None = None