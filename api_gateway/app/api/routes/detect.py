from fastapi import APIRouter, Depends, File, UploadFile

from api_gateway.app.core.security import require_auth
from api_gateway.app.api.routes.predict import predict

router = APIRouter(tags=["detect"], dependencies=[Depends(require_auth)])


@router.post("/detect")
async def detect(file: UploadFile = File(...)) -> dict:
    return await predict(file)
