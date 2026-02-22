import base64


def encode_to_base64(payload: bytes) -> str:
    return base64.b64encode(payload).decode("ascii")
