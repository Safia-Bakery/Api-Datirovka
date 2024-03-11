from sqlalchemy.orm import Session
import models
import schemas
from typing import Optional
import bcrypt

import pytz
from sqlalchemy.sql import func
from datetime import datetime,timedelta
from sqlalchemy import or_, and_, Date, cast
from uuid import UUID
from schemas import user_schema

from models import user

def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")

def get_user(db: Session, username: str):
    return db.query(user.Users).filter(user.Users.username == username).first()


def user_create(db:Session,form_data:user_schema.UserCreate):
    db_user = user.Users(username=form_data.username, hashed_password=hash_password(password=form_data.password), full_name=form_data.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user




