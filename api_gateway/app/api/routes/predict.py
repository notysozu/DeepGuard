from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from api_gateway.app.services.prediction_service import run_prediction
from database.session import get_db
from shared.schemas import PredictionResponse
from shared.security import get_current_user

router = APIRouter(tags=["predict"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Analyze media for synthetic manipulation",
    description="Upload an image or video to determine if it is authentic or deepfake using an ensemble of models."
)
async def predict(
    file: UploadFile = File(...),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Unknown file content type")
    if not file.content_type.startswith("image/") and not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only image and video files are supported")
    
    try:
        return await run_prediction(file=file, db=db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
