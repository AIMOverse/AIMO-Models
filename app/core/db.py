from sqlmodel import create_engine, SQLModel

from app.core.config import settings

import os

if os.environ.get("TESTING") == "True":
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
