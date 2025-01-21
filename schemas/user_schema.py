from pydantic import BaseModel, validator
from fastapi import Form, UploadFile, File
from typing import Optional, Annotated, Dict
from datetime import datetime, time
from fastapi import Form
from uuid import UUID


class UserCategoryGet(BaseModel):
    id:int
    name:Optional[str]=None

    class config:
        orm_mode = True



class UserBase(BaseModel):
    id:int
    username: str
    full_name: Optional[str] = None
    status: Optional[int] = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] =None
    categories: Optional[list[UserCategoryGet]]=None
    class config:
        orm_mode = True


class UserList(BaseModel):
    id:int
    username:str
    full_name:Optional[str]=None
    status: Optional[int] = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class config:
        orm_mode = True





class UserCreate(BaseModel):
    password:str
    username:str
    full_name:Optional[str] = None





class UserCategoryCreateRemove(BaseModel):
    user_id:int
    category_id:int





