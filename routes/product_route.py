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



@product_router.get('/v1/products/filter',response_model=Page[product_schema.GetProducts],summary="Filter products",tags=["Product"])
async def filter_products(name:Optional[str]=None,type:Optional[str]=None,id:Optional[UUID]=None,db:Session=Depends(get_db),current_user: user_schema.UserBase = Depends(get_current_user)):
    products = product_query.filter_products(db,name=name,type=type,id=id)
    return paginate(products)





