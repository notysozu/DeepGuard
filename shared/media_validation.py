from __future__ import annotations

from fastapi import HTTPException, UploadFile, status

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}
ALLOWED_AUDIO_TYPES = {"audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp4"}


class MediaValidationResult(dict):
    media_type: str
    content_type: str
    size_bytes: int


def _detect_media_type(content_type: str) -> str:
    if content_type in ALLOWED_IMAGE_TYPES:
        return "image"
    if content_type in ALLOWED_VIDEO_TYPES:
        return "video"
    if content_type in ALLOWED_AUDIO_TYPES:
        return "audio"
    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f"Unsupported content type: {content_type}",
    )


def _get_png_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width = int.from_bytes(data[16:20], "big")
    height = int.from_bytes(data[20:24], "big")
    return width, height


def _get_jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[0:2] != b"\xff\xd8":
        return None
    idx = 2
    while idx + 9 < len(data):
        if data[idx] != 0xFF:
            idx += 1
            continue
        marker = data[idx + 1]
        if marker in {0xC0, 0xC2}:
            block_len = int.from_bytes(data[idx + 2:idx + 4], "big")
            if idx + block_len + 2 <= len(data):
                height = int.from_bytes(data[idx + 5:idx + 7], "big")
                width = int.from_bytes(data[idx + 7:idx + 9], "big")
                return width, height
            return None
        if marker in {0xD8, 0xD9}:
            idx += 2
            continue
        block_len = int.from_bytes(data[idx + 2:idx + 4], "big")
        idx += 2 + block_len
    return None


def _validate_image_dimensions(data: bytes, content_type: str, max_pixels: int) -> None:
    dims: tuple[int, int] | None = None
    if content_type == "image/png":
        dims = _get_png_dimensions(data)
    elif content_type == "image/jpeg":
        dims = _get_jpeg_dimensions(data)

    if dims is None:
        return

    width, height = dims
    if width <= 0 or height <= 0 or width * height > max_pixels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image dimensions exceed allowed threshold",
        )


async def validate_media_upload(
    file: UploadFile,
    *,
    max_payload_mb: int,
    max_image_pixels: int = 50_000_000,
) -> tuple[bytes, MediaValidationResult]:
    data = await file.read()

    if not data:
        raise HTTPException(status_code=400, detail="Empty upload")

    max_bytes = max_payload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Payload exceeds {max_payload_mb} MB")

    content_type = (file.content_type or "").lower()
    media_type = _detect_media_type(content_type)

    if media_type == "image":
        _validate_image_dimensions(data, content_type, max_image_pixels)

    result: MediaValidationResult = {
        "media_type": media_type,
        "content_type": content_type,
        "size_bytes": len(data),
    }
    return data, result
