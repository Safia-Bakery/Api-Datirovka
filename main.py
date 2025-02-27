from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi import Depends, FastAPI, HTTPException,UploadFile,File,Form,Header,Request,status
from typing import Optional, TypeVar

from fastapi_pagination import paginate,Page,add_pagination,Params
from fastapi_pagination.customization import CustomizedPage, UseParamsFields
from fastapi.staticfiles import StaticFiles
from models.user import Base
from database import engine
from routes import user_route,product_route
from fastapi_pagination import set_page


T = TypeVar("T")


custompage = CustomizedPage[
    Page[T],
    UseParamsFields(size=1000)
]



app = FastAPI()
app.title = "Safia FastApi App"
app.version = "0.0.1"

#app.include_router(user_router)
Base.metadata.create_all(bind=engine)
app.mount("/files", StaticFiles(directory="files"), name="files")
app.include_router(user_route.user_router, tags=["User"])
app.include_router(product_route.product_router, tags=["Product"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Home"])
def message():
    """message get method"""
    return HTMLResponse("<h1>Fuck off man!</h1>")




add_pagination(app)

