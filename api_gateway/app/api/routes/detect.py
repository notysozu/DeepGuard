from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from api_gateway.app.services.prediction_service import run_prediction
from database.session import get_db
from shared.schemas import PredictionResponse
from shared.security import get_current_user

router = APIRouter(tags=["detect"])


@router.post("/detect", response_model=PredictionResponse)
async def detect(
    file: UploadFile = File(...),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await run_prediction(file=file, db=db)
