from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi_pagination import paginate, Page, add_pagination
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uuid import UUID
from services import (
    create_access_token,
    create_refresh_token,
    get_db,
    get_current_user,
    verify_password,
    verify_refresh_token
)
from typing import Optional
import models
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, Any
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import engine, SessionLocal
from queries import user_query
from schemas import user_schema

from dotenv import load_dotenv
import os
load_dotenv()



user_router = APIRouter()


@user_router.post("/login", summary="Create access and refresh tokens for user",tags=["User"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    db: Session = Depends(get_db),
):
    user = user_query.get_user(db, form_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )


    hashed_pass = user.hashed_password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    return {
        "access_token": create_access_token(user.username),
        "refresh_token": create_refresh_token(user.username),
    }



@user_router.post("/refresh", summary="Refresh access token",tags=["User"])
async def refresh(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    username = verify_refresh_token(refresh_token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        )
    return {"access_token": create_access_token(username)}

@user_router.post("/register",response_model=user_schema.UserBase, summary="Register a new user",tags=["User"])
async def register(
    form_data: user_schema.UserCreate,
    db: Session = Depends(get_db)):
    user = user_query.user_create(db=db, form_data=form_data),
    current_user: user_schema.UserBase = Depends(get_current_user)
    return user

@user_router.get("/me", response_model=user_schema.UserBase, summary="Get current user",tags=["User"])
async def get_current_user(db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    return current_user




@user_router.get("/users",response_model=list[user_schema.UserList],tags=["User"])
async  def get_users(db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    return user_query.get_users(db=db)

@user_router.get("/users/{id}",response_model=user_schema.UserBase,tags=["User"])
async  def get_one_user(
        id:int,
        db:Session=Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = user_query.get_one_user(db=db, id=id)
    user_categories_query = user_query.user_categories(db=db,id=id)
    query.categories = user_categories_query

    return query



@user_router.post("/users/category",tags=["User"])
async  def add_category_user(
    form_data: user_schema.UserCategoryCreateRemove,
    db:Session=Depends(get_db),
    current_user: user_schema.UserBase = Depends(get_current_user),
):
    query = user_query.add_category_user(db=db,form_data=form_data)
    return {'success':True}


@user_router.delete("/users/category",tags=["User"])
async  def add_delete_user(
    form_data: user_schema.UserCategoryCreateRemove,
    db:Session=Depends(get_db),
    current_user: user_schema.UserBase = Depends(get_current_user),
):

    query = user_query.remove_category_user(db=db,form_data=form_data)
    return {'success': True}





















