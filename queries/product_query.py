from models import products
from sqlalchemy.orm import Session
import schemas
from typing import Optional
import bcrypt
import pytz
from sqlalchemy.sql import func
from datetime import datetime
from uuid import UUID
from sqlalchemy import or_, and_, Date, cast, Integer
from sqlalchemy.exc import SQLAlchemyError
from schemas import product_schema


def create_product(db:Session,id:UUID,name:str,num:str,code:str,product_type:str,price:float,parent_id:Optional[str],main_unit:str,total_price:float,amount_left:float):
    item = products.Products(id=id,name=name,num=num,code=code,product_type=product_type,price=price,parent_id=parent_id,main_unit=main_unit,total_price=total_price,amount_left=amount_left)
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except SQLAlchemyError as e:
        db.rollback()
        return False


def get_product(db:Session,id:UUID):
    return db.query(products.Products).filter(products.Products.id == id).first()

def get_group(db:Session,id:UUID):
    return db.query(products.Groups).filter(products.Groups.id == id).first()

def create_group(db:Session,id:UUID,name:str,description:str,num:Optional[str],code:Optional[str],parent_id:Optional[str],category:Optional[str]):
    item = products.Groups(id=id,name=name,description=description,num=num,code=code,parent_id=parent_id,category=category)
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except SQLAlchemyError as e:
        db.rollback()
        return False


def get_product_parent(db:Session,parent_id:UUID):
    return db.query(products.Products).filter(products.Products.parent_id == parent_id).first()


def get_child_products(db:Session,parent_id:Optional[UUID]=None):
    return db.query(products.Products).filter(products.Products.parent_id == parent_id).filter(products.Products.status==1).all()

def get_child_groups(db:Session,parent_id:Optional[UUID]=None):
    return db.query(products.Groups).filter(products.Groups.parent_id == parent_id).filter(products.Groups.status==1).all() 


def update_product(db:Session,form_data:product_schema.Update_status):
    item = db.query(products.Products).filter(products.Products.id == id).first()
    if form_data.status is not None:
        item.status = form_data.status
    if form_data.validity is not None:
        item.validity = form_data.validity
    if form_data.description is not None:
        item.description = form_data.description
    db.commit()
    db.refresh(item)
    return item

def update_group(db:Session,id:UUID,status):
    item = db.query(products.Groups).filter(products.Groups.id == id).first()
    item.status = status
    db.commit()
    db.refresh(item)
    return item


def filter_products(db:Session,name:str):
    item = db.query(products.Products).filter(products.Products.name.like(f"%{name}%")).all()
    return item