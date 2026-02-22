import uuid


def new_request_id() -> str:
    return str(uuid.uuid4())
