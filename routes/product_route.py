from fastapi import APIRouter
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi_pagination import paginate, Page, add_pagination
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, TypeVar
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uuid import UUID
from services import (
    create_access_token,
    create_refresh_token,
    get_db,
    get_current_user,
    verify_password,
    verify_refresh_token,
    getgroups,
    getproducts,
    authiiko
)
from typing import Optional
import models
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, Any
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import engine, SessionLocal
from queries import product_query
from schemas import user_schema,product_schema



product_router = APIRouter()




T = TypeVar("T")


custompage = CustomizedPage[
    Page[T],
    UseParamsFields(size=50,max_size=1000)
]



@product_router.get("/v1/products/synch", summary="Synch products with iiko",tags=["Product"])
async def synch_products(db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    iiko_key = authiiko()
    products = getproducts(iiko_key)
    for i in products:

        if i['type'] in ['GOODS','DISH']:
            #if not product_query.get_product(db,id=i["id"]):
                product_query.create_product(db,id=i["id"],name=i["name"],num=i["num"],code=i["code"],product_type=i["type"],price=i["defaultSalePrice"],parent_id=i["parent"],main_unit=i["mainUnit"],total_price=i["estimatedPurchasePrice"],amount_left=None)
    del products
    groups = getgroups(iiko_key)
    for i in groups:
        
        if product_query.get_product_parent(db,parent_id=i["id"]):
           #if not product_query.get_group(db,id=i["id"]):
                product_query.create_group(db,id=i["id"],name=i["name"],description=i["description"],num=i["num"],code=i["code"],parent_id=i["parent"],category=i["category"])
    del groups
    return {"message":"Synch products with iiko"}



@product_router.get("/v1/products", summary="Get all products",tags=["Product"])
async def get_all_products(parent_id:Optional[UUID]=None,name:Optional[str]=None,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    products = product_query.get_child_products(db,parent_id=parent_id,name=name)
    groups = product_query.get_child_groups(db,parent_id=parent_id,name=name)
    return {"products":products,"groups":groups}



@product_router.put('/v1/products',summary="Update product status",tags=["Product"])
async def update_product_status(form_data:product_schema.Update_status,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    return product_query.update_product(db,form_data=form_data)


@product_router.put('/v1/groups',summary="Update group status",tags=["Product"])
async def update_group_status(form_data:product_schema.Update_status,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    return product_query.update_group(db,id=form_data.id,status=form_data.status)



@product_router.get('/v1/products/filter',response_model=custompage[product_schema.GetProducts],summary="Filter products",tags=["Product"])
async def filter_products(name:Optional[str]=None,type:Optional[str]=None,id:Optional[UUID]=None,category_id:Optional[int]=None,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    products = product_query.filter_products(db,name=name,type=type,id=id,category_id=category_id)
    return paginate(products)


# -----Categories create

@product_router.post('/v1/category',summary="Create category",tags=["Category"])
async def create_category(form_data:product_schema.CreateCategory,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    return product_query.create_category(db,form_data=form_data)

# -----Categories update 

@product_router.put('/v1/category',summary="Update category",tags=["Category"])
async def update_category(form_data:product_schema.UpdateCategory,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    return product_query.update_category(db,form_data=form_data)


# -----Categories filter

@product_router.get('/v1/category',response_model=Page[product_schema.GetCategory],summary="Filter categories",tags=["Category"])
async def filter_categories(name:Optional[str]=None,id:Optional[int]=None,status:Optional[int]=None,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    categories = product_query.filter_categories(db,name=name,id=id,status=status,user_id=current_user.id)
    return paginate(categories)



@product_router.get('/v2/category',response_model=Page[product_schema.GetCategory],summary="Filter categories",tags=["Category"])
async def filter_categories_v2(name:Optional[str]=None,id:Optional[int]=None,status:Optional[int]=None,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    if current_user.id==10:
        categories = product_query.filter_categories_v2_factory(db,name=name,id=id,status=1)
    else:
        categories = product_query.filter_categories(db, name=name, id=id, status=1,user_id=current_user.id)
    return paginate(categories)


@product_router.get('/v1/categories/products',response_model=list[product_schema.GetCategoryFull],tags=["Category"])
async def filter_categories(
                            name:Optional[str]=None,
                            db:Session=Depends(get_db),
                            current_user: user_schema.UserBase = Depends(get_current_user)):
    categories = product_query.get_all_active_categories(db,name=name,current_user_id=current_user.id)
    return categories




@product_router.post('/factory/products',response_model=product_schema.GetFactoryProduct,tags=['Factory'])
async  def create_factory_products(
            form_data:product_schema.CreateFactoryProduct,
            db:Session=Depends(get_db),
            current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.create_factory_product(db=db,form_data=form_data)
    return query


@product_router.put('/factory/products',response_model=product_schema.GetFactoryProduct,tags=['Factory'])
async  def update_factory_product(
        id:UUID,
        form_data:product_schema.UpdateFactoryProduct,
        db:Session=Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.update_factory_product(db=db,id=id,form_data=form_data)
    return query


@product_router.get('/factory/products/{id}',response_model=product_schema.GetFactoryProduct,tags=['Factory'])
async  def get_factory_product(
        id:UUID,
        db: Session = Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.get_factory_product(db=db,id=id)
    return query


@product_router.get('/factory/category/products',response_model=list[product_schema.GetFactoryProduct],tags=['Factory'])
async  def get_factory_products(
        category_id:int,
        name:Optional[str]=None,
        db: Session = Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.get_factory_products(db=db,name=name,category_id=category_id)
    return query



@product_router.post('/factory/category',response_model=product_schema.GetCategory,tags=['Factory'])
async  def create_factory_categories(
        form_data:product_schema.CreateCategory,
        db: Session = Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.create_factory_category(form_data=form_data,db=db)
    return query

@product_router.put('/factory/category',response_model=product_schema.GetCategory,tags=['Factory'])
async  def update_factory_categories(
        id:int,
        form_data:product_schema.UpdateFactoryCategory,
        db: Session = Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.update_factory_category(db=db,form_data=form_data,id=id)
    return query



@product_router.get('/factory/category/{id}',response_model=product_schema.GetCategory,tags=['Factory'])
async def get_one_category(
        id:int,
        db: Session = Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.get_one_category(db=db,id=id)
    return query


@product_router.get('/factory/category',response_model=list[product_schema.GetCategory],tags=['Factory'])
async  def get_categories_factory(
        db: Session = Depends(get_db),
        current_user: user_schema.UserBase = Depends(get_current_user)
):
    query = product_query.get_factory_categories(db=db)
    return query








