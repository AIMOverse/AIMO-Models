import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_purposes_only"
os.environ["ADMIN_API_KEY"] = "test_admin_api_key"
os.environ["DEFAULT_API_QUOTA"] = "100"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"

from app.core.config import settings