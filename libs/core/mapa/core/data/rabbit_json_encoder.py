from collections import deque
from datetime import datetime
from decimal import Decimal
import json
import uuid
import base64

class RabbitJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return str(obj)
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, deque):
            return list(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('ascii')
        return json.JSONEncoder.default(self, obj)