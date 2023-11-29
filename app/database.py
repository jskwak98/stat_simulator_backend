from sqlalchemy import create_engine, MetaData
from databases import Database

DATABASE_URL = "sqlite:///./test.db"  # Path to your SQLite database

# 동시성을 위해서 check_same_thread를 해야한다.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata = MetaData()

database = Database(DATABASE_URL)
