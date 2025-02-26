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
    id = Column(UUID(as_uuid=True), primary_key=True, index=True,default=uuid.uuid4)
    name = Column(String, index=True,nullable=True)
    num = Column(String,nullable=True)
    code = Column(String,nullable=True)
    product_type = Column(String,nullable=True)
    price = Column(Float,nullable=True)
    parent_id = Column(UUID(as_uuid=True),nullable=True)
    main_unit = Column(String,nullable=True)
    total_price =  Column(Float,nullable=True)
    amount_left =  Column(Float,nullable=True)
    status = Column(Integer,default=1)
    description = Column(String,nullable=True)
    validity = Column(Integer,nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    qr = Column(String,nullable=True)
    category_id = Column(BIGINT, ForeignKey("categories.id"),nullable=True)
    category = relationship("Categories", back_populates="product")
    is_returnable = Column(Integer,nullable=True)
    temperature = Column(String,nullable=True)






class Categories(Base):
    __tablename__ = "categories"
    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String,nullable=True)
    status = Column(Integer,default=1)
    is_factory = Column(Integer,nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    product = relationship("Products", back_populates="category")
    user_cat = relationship('UserCategoryRelations',back_populates='user_category')





class UserCategoryRelations(Base):
    __tablename__ = 'user_category_relations'
    id = Column(BIGINT, primary_key=True, index=True)
    user_id = Column(BIGINT,ForeignKey('users.id'))
    user = relationship('Users',back_populates='category')
    category_id = Column(BIGINT,ForeignKey('categories.id'))
    user_category = relationship('Categories',back_populates='user_cat')


