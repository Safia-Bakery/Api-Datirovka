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
from schemas.product_schema import (
CreateFactoryProduct,
GetFactoryProduct,
UpdateFactoryProduct,
CreateCategory,
UpdateCategory,
UpdateFactoryCategory
)

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


def get_child_products(db:Session,name,parent_id:Optional[UUID]=None):
    item = db.query(products.Products).filter(products.Products.parent_id == parent_id).filter(products.Products.status==1)
    if name is not None:
        item = item.filter(products.Products.name.ilike(f"%{name}%"))
    return item.all()

def get_child_groups(db:Session,name,parent_id:Optional[UUID]=None):
    item = db.query(products.Groups).filter(products.Groups.parent_id == parent_id).filter(products.Groups.status==1)
    if name is not None:
        item = item.filter(products.Products.name.ilike(f"%{name}%"))
    return item.all()


def update_product(db:Session,form_data:product_schema.Update_status):
    item = db.query(products.Products).filter(products.Products.id == form_data.id).first()
    if form_data.status is not None:
        item.status = form_data.status
    if form_data.validity is not None:
        item.validity = form_data.validity
    if form_data.description is not None:
        item.description = form_data.description
    if form_data.qr is not None:
        item.qr = form_data.qr
    if form_data.category_id is not None:
        item.category_id = form_data.category_id
    if form_data.name is not None:
        item.name = form_data.name
    db.commit()
    db.refresh(item)
    return item

def update_group(db:Session,id:UUID,status):
    item = db.query(products.Groups).filter(products.Groups.id == id).first()
    item.status = status
    db.commit()
    db.refresh(item)
    return item


def filter_products(db:Session,name,type,id,category_id):
    item = db.query(products.Products)
    if name is not None:
        item = item.filter(products.Products.name.ilike(f"%{name}%"))   
    if type is not None:
        item = item.filter(products.Products.product_type == type)
    if id is not None:
        item = item.filter(products.Products.id == id)
    if category_id is not None:
        item = item.filter(products.Products.category_id == category_id)
    item = item.filter(products.Products.status==1)
    return item.all()



def create_category(db:Session,form_data:product_schema.CreateCategory):
    item = products.Categories(name=form_data.name,status=form_data.status)
    try:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
    except SQLAlchemyError as e:
        db.rollback()
        return False

def update_category(db:Session,form_data:product_schema.UpdateCategory):
    item = db.query(products.Categories).filter(products.Categories.id == form_data.id).first()
    if form_data.name is not None:
        item.name = form_data.name
    if form_data.status is not None:
        item.status = form_data.status
    db.commit()
    db.refresh(item)
    return item


def filter_categories(db:Session,name,status,id):
    item = db.query(products.Categories)
    if name is not None:
        item = item.filter(products.Categories.name.ilike(f"%{name}%"))   
    if status is not None:
        item = item.filter(products.Categories.status == status)
    if id is not None:
        item = item.filter(products.Categories.id == id)
    return item.filter(products.Categories.is_factory!=1).all()



def get_all_active_categories(db:Session,name,current_user_id):
    item = db.query(products.Categories).join(products.Products)
    if name is not None:
        item = item.filter(products.Products.name.ilike(f"%{name}%"))
    item = item.filter(products.Categories.status == 1).join(products.Categories.user_cat).filter(products.UserCategoryRelations.user_id==current_user_id).all()
    #declare items products again
    if name is not None:
        for index,category in enumerate(item):
            item[index].product = db.query(products.Products).filter(and_(products.Products.category_id == category.id, products.Products.name.ilike(f"%{name}%"))).all()
    return item



def create_factory_product(db:Session,form_data:CreateFactoryProduct):
    query = products.Products(name=form_data.name,validity=form_data.validity,is_returnable=form_data.is_returnable)
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


def update_factory_product(db:Session,form_data:UpdateFactoryProduct,id):
    query = db.query(products.Products).filter(products.Products.id==id).first()
    if query:
        query.name=form_data.name
        query.is_returnable= form_data.is_returnable
        query.validity=form_data.validity
        db.commit()
        db.refresh(query)

    return query

def get_factory_products(db:Session,name:Optional[str]=None,category_id:Optional[int]=None):
    query = db.query(products.Products)
    if name is not None:
        query = query.filter(products.Products.name.ilike(f"%{name}%"))
    if category_id is not None:
        query = query.filter(products.Products.category_id==category_id)

    return query.all()


def get_factory_product(db:Session,id):
    query = db.query(products.Products).filter(products.Products.id==id).first()
    return query


def create_factory_category(db:Session,form_data:CreateCategory):
    query = products.Categories(
        name=form_data.name,
        status=form_data.status,
        is_factory=1
    )
    db.add(query)
    db.commit()
    db.refresh(query)


def update_factory_category(db:Session,form_data:UpdateFactoryCategory,id):
    query = db.query(products.Categories).filter(products.Categories.id==id).first()
    if query:
        query.name=form_data.name
        query.status=form_data.status
        db.commit()
        db.refresh(query)
    return query



def get_factory_categories(db:Session):
    query = db.query(products.Categories).filter(products.Categories.is_factory==1).all()
    return query


def get_one_category(db:Session,id):
    query = db.query(products.Categories).filter(products.Categories.id==id).first()
    return query












