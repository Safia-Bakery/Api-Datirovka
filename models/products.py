from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
    Boolean,
    BIGINT,
    Table,
    Time,
    JSON,
    VARCHAR,
    Date,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from datetime import datetime
import pytz
import uuid
from .user import Base
timezonetash = pytz.timezone("Asia/Tashkent")



class Groups(Base):
    __tablename__ = "groups"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String,nullable=True)
    status = Column(Integer, default=1)
    num = Column(String,nullable=True)
    code = Column(String,nullable=True)
    parent_id = Column(UUID(as_uuid=True),nullable=True)
    category = Column(String,nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Products(Base):   
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, index=True,nullable=True  )
    num = Column(String,nullable=True)
    code = Column(String,nullable=True)
    product_type = Column(String,nullable=True)
    price = Column(Float,nullable=True)
    parent_id = Column(UUID(as_uuid=True),nullable=True)
    main_unit = Column(String,nullable=True)
    total_price =  Column(Float,nullable=True)
    amount_left =  Column(Float,nullable=True)
    status = Column(Integer,default=1)

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())




