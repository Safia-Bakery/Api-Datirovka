from datetime import datetime, timedelta
import pytz
from jose import jwt
from passlib.context import CryptContext
import bcrypt
import schemas
from sqlalchemy.orm import Session
from typing import Union, Any
from fastapi import (
    Depends,
    HTTPException,
    status,
)
from database import engine, SessionLocal
from pydantic import ValidationError
from fastapi.security import OAuth2PasswordBearer
import xml.etree.ElementTree as ET
import os
from schemas import user_schema
from queries import user_query as crud
from dotenv import load_dotenv
import requests

load_dotenv()

BASE_URL = os.environ.get("BASE_URL")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY") # should be kept secret
ALGORITHM = os.environ.get("ALGORITHM")
LOGIN_IIKO = os.environ.get("LOGIN_IIKO")
PASSWORD_IIKO = os.environ.get("PASSWORD_IIKO")


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt



async def get_current_user(
    token: str = Depends(reuseable_oauth), db: Session = Depends(get_db)
) -> user_schema.UserBase:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        expire_date = payload.get("exp")
        sub = payload.get("sub")
        if datetime.fromtimestamp(expire_date) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user: Union[dict[str, Any], None] = crud.get_user(db, sub)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return user

def verify_refresh_token(refresh_token: str) -> Union[str, None]:
    try:
        payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        expire_date = payload.get("exp")
        sub = payload.get("sub")
        if datetime.fromtimestamp(expire_date) < datetime.now():
            return None
    except (jwt.JWTError, ValidationError):
        return None
    return sub


def authiiko():
    data = requests.get(
        f"{BASE_URL}/resto/api/auth?login={LOGIN_IIKO}&pass={PASSWORD_IIKO}"
    )

    key = data.text
    return key


def getgroups(key):
    groups = requests.get(
        f"{BASE_URL}/resto/api/v2/entities/products/group/list?key={key}"
    ).json()
    return groups



def getproducts(key):
    products = requests.get(
        f"{BASE_URL}/resto/api/v2/entities/products/list?key={key}"
    ).json()

    return products



