import hashlib


def generate_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()
