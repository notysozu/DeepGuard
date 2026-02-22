from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from api_gateway.app.services.prediction_service import run_prediction
from database.session import get_db
from shared.schemas import PredictionResponse
from shared.security import get_current_user

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    _: object = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await run_prediction(file=file, db=db)
