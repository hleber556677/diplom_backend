from typing import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


if not settings.database_url:
    raise RuntimeError(
        "Database URL is not configured. Set SUPABASE_DATABASE_URL or DATABASE_URL "
        "to the PostgreSQL connection string from Supabase."
    )

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
        db.connection()
    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable. Check the Supabase connection settings and try again.",
        ) from exc

    try:
        yield db
    finally:
        db.close()
