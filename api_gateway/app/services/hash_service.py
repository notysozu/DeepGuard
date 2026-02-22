import json
import sqlite3
from pathlib import Path

from api_gateway.app.core.config import settings


class PredictionStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS predictions (
                    request_id TEXT PRIMARY KEY,
                    media_hash TEXT NOT NULL UNIQUE,
                    media_type TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    ensemble_method TEXT NOT NULL,
                    inference_time REAL NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def find_by_hash(self, media_hash: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT response_json FROM predictions WHERE media_hash = ?",
                (media_hash,),
            ).fetchone()
            if not row:
                return None
            return json.loads(row["response_json"])

    def insert(self, payload: dict, media_hash: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO predictions (
                    request_id, media_hash, media_type, verdict, confidence,
                    ensemble_method, inference_time, response_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["request_id"],
                    media_hash,
                    payload["media_type"],
                    payload["verdict"],
                    payload["confidence"],
                    payload["ensemble_method"],
                    payload["inference_time"],
                    json.dumps(payload),
                ),
            )
            conn.commit()

    def list_history(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT request_id, media_type, verdict, confidence, ensemble_method,
                       inference_time, created_at
                FROM predictions
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_by_request_id(self, request_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT response_json FROM predictions WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            if not row:
                return None
            return json.loads(row["response_json"])


store = PredictionStore(settings.db_path)
