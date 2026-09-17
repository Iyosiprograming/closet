from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    password: str


class LoginUserSchema(UserCreateSchema):
    pass
class UserCreateResponseSchema(BaseModel):
    id: int
    username: str


class AddApiKey(BaseModel):
    gemini_api_key: str
    openweather_api_key: str


class AddLocation(BaseModel):
    location: str | None = None