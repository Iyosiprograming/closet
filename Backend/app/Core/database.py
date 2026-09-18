from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.Core.paths import database_path, ensure_directories


# The database lives in a writable directory that depends on how the app runs:
# `Backend/closet.db` from source, `%LOCALAPPDATA%\ClosetAI\data\closet.db` when
# packaged. See app/Core/paths.py.
ensure_directories()

DATABASE_FILE = database_path()

# Built with URL.create so spaces or other awkward characters in the path are
# escaped correctly.
DATABASE_URL = URL.create("sqlite", database=str(DATABASE_FILE))


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()