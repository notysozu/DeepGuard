import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.crud import get_by_request_id, get_history
from database.session import get_db
from shared.schemas import HistoryItem, HistoryResponse
from shared.security import require_role

router = APIRouter(tags=["history"])


@router.get("/history", response_model=HistoryResponse)
def history(
    limit: int = 100,
    _: object = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    rows = get_history(db, limit=limit)
    items = [
        HistoryItem(
            id=r.id,
            media_type=r.media_type,
            sha256_hash=r.sha256_hash,
            verdict=r.verdict,
            confidence=r.confidence,
            ensemble_method=r.ensemble_method,
            inference_time=r.inference_time,
            created_at=r.created_at,
        )
        for r in rows
    ]
    return HistoryResponse(items=items)


@router.get("/history/{request_id}")
def history_item(
    request_id: str,
    _: object = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    row = get_by_request_id(db, request_id=request_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Request ID not found")
    return json.loads(row.full_response_json)
