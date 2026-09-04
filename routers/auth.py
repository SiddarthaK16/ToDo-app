import os
from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import  HTTPException, APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from starlette import status
from database import SessionLocal
from models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

bcrypt_context= CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer= OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_active: bool
    first_name: str
    last_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db):
    user= db.query(Users).filter(Users.username==username).first()

    if not user:
        return False
    if not bcrypt_context.verify( password, user.hashed_password,):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):

    encode= {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        return { "username": username, "id": user_id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")



db_dependency= Annotated[Session,Depends(get_db)]
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model= Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        is_active=create_user_request.is_active,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
    )

    if create_user_model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,)

    db.add(create_user_model)
    db.commit()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm,Depends()],db: db_dependency):
    user= authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    token= create_access_token(user.username, user.id, timedelta(minutes=30))

    return { "access_token": token, "token_type": "bearer" }

