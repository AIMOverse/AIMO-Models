import os
from pathlib import Path

# 测试环境变量设置
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_purposes_only"
os.environ["ADMIN_API_KEY"] = "test_admin_api_key"
os.environ["DEFAULT_API_QUOTA"] = "100"  # 测试中使用较小的配额
os.environ["REDIS_URL"] = "redis://localhost:6379/0"  # Redis连接

# 必须在导入settings之前设置环境变量
from app.core.config import settings