from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "mysql+aiomysql://user:password@localhost:3307/your_database_name"

engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(bind=engine, class_=AsyncSession)
async def get_session():
    session = session_factory()
    return session

class Base(DeclarativeBase):
    pass