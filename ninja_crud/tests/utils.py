import datetime
import uuid


def default_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, (dict, list, str, int, float, bool, type(None))):
        return obj
    raise TypeError(f"Type {type(obj)} not serializable")
