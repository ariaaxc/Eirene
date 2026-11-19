from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "mysql+aiomysql://root:root_password@127.0.0.1:3307/eirene"


engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(bind=engine, class_=AsyncSession)
async def get_session():
    session = session_factory()
    return session

class Base(DeclarativeBase):
    pass