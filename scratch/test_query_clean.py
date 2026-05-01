import sys
import os

# Add libs to path
sys.path.append(r"d:\Projeler\KABART\10_MAPA\mappa-enterprise-server\libs\core")
sys.path.append(r"d:\Projeler\KABART\10_MAPA\mappa-enterprise-server\libs\app")

from mapa.core.data.query_args import QueryArgs
import json

data_str = '{"where":[{"field":"name","op":"contains","value":"adm"}],"limit":10}'
print(f"Testing data: {data_str}")

try:
    qa = QueryArgs.model_validate_json(data_str)
    print("SUCCESS validation")
    print(qa.model_dump())
except Exception as e:
    print("FAILED validation")
    print(e)
