from sqlmodel import create_engine, SQLModel

from app.core.config import settings

import os

if os.environ.get("TESTING") == "True":
    DATABASE_URL = "sqlite:///:memory:"
else:
    DATABASE_URL = "postgresql://ai_model:A1-M0Dn189z2d86@localhost:5432/ai_model"

engine = create_engine(DATABASE_URL)

# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
