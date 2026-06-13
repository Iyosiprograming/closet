from unittest.mock import MagicMock
from app.Services.user_service import UserService
from app.Schemas.user_schema import UserCreateSchema

from unittest.mock import MagicMock
from app.Services.user_service import UserService
from app.Models.user_model import User
from app.Schemas.user_schema import UserCreateSchema

def test_create_new_user():
    mock_db = MagicMock()

    mock_db.query.return_value.filter.return_value.first.return_value = None

    service = UserService(mock_db)

    user_data = UserCreateSchema(
        tg_id=123,
        tg_username="iyosi"
    )

    response = service.create_user(user_data)

    assert response.message == (
        "Welcome, iyosi! Your account has been created."
    )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()




def test_create_user_existing_user():
    mock_db = MagicMock()

    existing_user = User(
        tg_id=123,
        tg_username="iyosi"
    )

    mock_db.query.return_value.filter.return_value.first.return_value = existing_user

    service = UserService(mock_db)

    user_data = UserCreateSchema(
        tg_id=123,
        tg_username="iyosi"
    )

    response = service.create_user(user_data)

    assert response.message == "Welcome Back, iyosi!"