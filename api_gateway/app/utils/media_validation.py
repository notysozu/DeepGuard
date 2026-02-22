from fastapi import HTTPException, UploadFile

_ALLOWED_TYPES = {
    "image": {"image/jpeg", "image/png", "image/webp"},
    "video": {"video/mp4", "video/quicktime", "video/x-msvideo"},
    "audio": {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"},
}



def infer_media_type(content_type: str) -> str:
    if not content_type:
        raise HTTPException(status_code=400, detail="Missing content-type")
    for media_type, allowed in _ALLOWED_TYPES.items():
        if content_type.lower() in allowed:
            return media_type
    raise HTTPException(status_code=415, detail=f"Unsupported content type: {content_type}")



def validate_upload(file: UploadFile, data: bytes, max_payload_mb: int) -> str:
    media_type = infer_media_type(file.content_type or "")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    max_bytes = max_payload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File exceeds {max_bytes} bytes")
    return media_type
