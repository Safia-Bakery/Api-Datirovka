from pydantic import BaseModel, validator
from fastapi import Form, UploadFile, File
from typing import Optional, Annotated, Dict
from datetime import datetime, time
from fastapi import Form
from uuid import UUID


class GetCategory(BaseModel):   
    id:int
    name:str    
    status:Optional[int]=1
    class config:
        orm_mode = True 





class Update_status(BaseModel):
    id:UUID
    status: Optional[int] = None
    validity:Optional[int]=None
    description:Optional[str]=None
    qr:Optional[str]=None
    category_id:Optional[int]=None
    name : Optional[str]=None


class GetProducts(BaseModel):
    id:UUID
    name:str
    num:Optional[str]=None
    code:Optional[str]=None
    product_type:str
    price:Optional[float]=None
    parent_id:Optional[UUID]=None
    main_unit:Optional[str]=None
    total_price:Optional[float]=None
    amount_left:Optional[float]=None
    status:Optional[int]=None
    description:Optional[str]=None
    validity :Optional[int]=None
    qr:Optional[str]=None
    category_id:Optional[int]=None
    category:Optional[GetCategory]=None
    class config:
        orm_mode = True




class CreateCategory(BaseModel):
    name:str
    status:Optional[int]=1  
    class config:
        orm_mode = True 


class UpdateCategory(BaseModel):    
    id:int
    name:Optional[str]=None
    status:Optional[int]=1
    class config:
        orm_mode = True
