from app.Schemas.user_schema import UserCreateSchema, UserCreateResponseSchema

def test_user_create_schema():
    user_data = {
        "tg_id": 123456789,
        "tg_username": "testuser",
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.tg_id == 123456789
    assert user_schema.tg_username == "testuser"

def test_user_create_response_schema():
    response_data = {
        "message": "Welcome, testuser! Your account has been created."
    }
    response_schema = UserCreateResponseSchema(**response_data)
    assert response_schema.message == "Welcome, testuser! Your account has been created."