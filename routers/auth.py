from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, EmailStr
from starlette import status

from models import Users

router = APIRouter()

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_active: bool
    first_name: str
    last_name: str
    role: str
@router.post("/auth/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest):
    create_user_model= Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        is_active=create_user_request.is_active,
        role=create_user_request.role,
        hashed_password=create_user_request.password
    )

    if create_user_model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,)

    return create_user_model

