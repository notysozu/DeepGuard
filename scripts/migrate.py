#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from database.session import engine

MIGRATIONS_DIR = Path("database/migrations")



def ensure_migrations_table() -> None:
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
                """
            )
        )



def applied_versions() -> set[str]:
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()
    return {row[0] for row in rows}



def apply_migration(version: str, sql_text: str) -> None:
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    with engine.begin() as conn:
        for stmt in statements:
            try:
                conn.execute(text(stmt))
            except Exception as exc:
                msg = str(exc).lower()
                if "duplicate column" in msg or "already exists" in msg:
                    continue
                raise
        conn.execute(
            text("INSERT INTO schema_migrations(version) VALUES (:version)"),
            {"version": version},
        )



def main() -> None:
    ensure_migrations_table()
    applied = applied_versions()

    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = path.name
        if version in applied:
            continue
        sql_text = path.read_text(encoding="utf-8")
        apply_migration(version, sql_text)
        print(f"Applied migration: {version}")

    print("Migrations complete.")


if __name__ == "__main__":
    main()
