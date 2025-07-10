from sqlmodel import create_engine, SQLModel

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)


# Create the database and tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
