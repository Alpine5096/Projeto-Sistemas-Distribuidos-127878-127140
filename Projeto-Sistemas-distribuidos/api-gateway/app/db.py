from sqlalchemy import create_engine, MetaData
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://micro:micropass@postgres:5432/microsvc")
engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()
