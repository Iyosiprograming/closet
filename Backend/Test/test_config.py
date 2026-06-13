from app.config import Config
import pytest

def test_db_url():
    assert Config.DB_URL == "sqlite:///./app.db"