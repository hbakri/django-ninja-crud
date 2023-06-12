import datetime
import uuid


def default_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    else:  # pragma: no cover
        raise TypeError(f"Type {type(obj)} not serializable")
