from app.core.db import create_db_and_tables
# Import all entities to ensure tables are created
from app.entity.User import User
from app.entity.invitation_code import InvitationCode

if __name__ == "__main__":
    create_db_and_tables()
