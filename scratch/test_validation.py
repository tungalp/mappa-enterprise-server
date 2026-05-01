from mapa.core.data.query_args import QueryArgs
from pydantic import TypeAdapter
import json

query_str = '{"where":[{"type":"filter","field":"name","op":"contains","value":"adm"}],"limit":10}'
query_dict = json.loads(query_str)

try:
    args = TypeAdapter(QueryArgs).validate_python(query_dict)
    print("Validation successful")
    print(args.model_dump())
except Exception as e:
    print(f"Validation failed: {e}")
