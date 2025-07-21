# 统一用户系统 (Unified User System)

## 概述

新的统一用户系统通过单一的 `User` 类支持邮箱和钱包两种登录方式，用户可以：
- 仅使用邮箱注册和登录
- 仅使用钱包地址注册和登录  
- 同时绑定邮箱和钱包地址，任选其一登录

## 核心特性

### User 实体
- **灵活认证**: 支持邮箱、钱包地址或两者兼有
- **邮箱验证**: 内置邮箱验证机制
- **状态管理**: 用户激活/停用状态
- **登录追踪**: 记录最后登录时间

### 主要字段
```python
class User(SQLModel, table=True):
    user_id: str                    # 唯一用户标识
    email: Optional[str]            # 邮箱地址（可选）
    wallet_address: Optional[str]   # 钱包地址（可选）
    invitation_code: Optional[str]  # 邀请码
    email_verified: bool            # 邮箱是否已验证
    is_active: bool                 # 用户是否激活
    created_at: datetime            # 创建时间
    last_login: Optional[datetime]  # 最后登录时间
```

## 使用方法

### 1. 创建用户

```python
from app.services.user_service import UserService

# 仅邮箱注册
user = UserService.create_user_with_email("user@example.com")

# 仅钱包注册  
user = UserService.create_user_with_wallet("0x1234...5678")

# 同时绑定邮箱和钱包
user = UserService.create_user_with_both("user@example.com", "0x1234...5678")
```

### 2. 登录验证

```python
# 统一登录接口（自动识别邮箱或钱包）
can_login, user = UserService.can_user_login("user@example.com")
can_login, user = UserService.can_user_login("0x1234...5678")

if can_login:
    UserService.update_last_login(user.user_id)
    print(f"用户 {user.user_id} 登录成功")
```

### 3. 邮箱验证

```python
import datetime

# 发送验证码
expires_at = datetime.datetime.now() + datetime.timedelta(minutes=15)
UserService.set_email_verification_code(user.user_id, "123456", expires_at)

# 验证邮箱
success = UserService.verify_email(user.user_id, "123456")
```

### 4. 添加认证方式

```python
# 为现有用户添加邮箱
UserService.add_email_to_user(user.user_id, "new@example.com")

# 为现有用户添加钱包
UserService.add_wallet_to_user(user.user_id, "0xnew...address")
```

## 业务场景

### 场景1: 邮箱用户绑定钱包
```python
# 1. 用户邮箱注册
user = UserService.create_user_with_email("alice@example.com")

# 2. 验证邮箱
UserService.set_email_verification_code(user.user_id, "123456", expires_at)
UserService.verify_email(user.user_id, "123456")

# 3. 后续绑定钱包
UserService.add_wallet_to_user(user.user_id, "0xalice...wallet")

# 4. 现在可以用邮箱或钱包登录
UserService.can_user_login("alice@example.com")      # ✅ 成功
UserService.can_user_login("0xalice...wallet")       # ✅ 成功
```

### 场景2: 钱包用户绑定邮箱
```python
# 1. 用户钱包注册
user = UserService.create_user_with_wallet("0xbob...wallet")

# 2. 后续绑定邮箱
UserService.add_email_to_user(user.user_id, "bob@example.com")

# 3. 验证邮箱
UserService.verify_email(user.user_id, "123456")

# 4. 现在可以用钱包或邮箱登录
UserService.can_user_login("0xbob...wallet")         # ✅ 成功
UserService.can_user_login("bob@example.com")        # ✅ 成功
```

### 场景3: 同时注册
```python
# 直接创建双重认证用户
user = UserService.create_user_with_both(
    "charlie@example.com", 
    "0xcharlie...wallet"
)

# 验证邮箱后即可使用两种方式登录
UserService.verify_email(user.user_id, "123456")
```

## API接口示例

### 注册接口
```python
@app.post("/register/email")
def register_with_email(email: str, invitation_code: str = None):
    user = UserService.create_user_with_email(email, invitation_code)
    # 发送验证邮件...
    return {"user_id": user.user_id, "email": user.email}

@app.post("/register/wallet")  
def register_with_wallet(wallet_address: str, invitation_code: str = None):
    user = UserService.create_user_with_wallet(wallet_address, invitation_code)
    return {"user_id": user.user_id, "wallet_address": user.wallet_address}
```

### 登录接口
```python
@app.post("/login")
def login(identifier: str):  # 邮箱或钱包地址
    can_login, user = UserService.can_user_login(identifier)
    if can_login:
        UserService.update_last_login(user.user_id)
        return {"success": True, "user_id": user.user_id}
    return {"success": False, "message": "Invalid credentials"}
```

## 文件结构

```
app/
├── entity/
│   ├── User.py              # 新的统一用户实体
├── services/
│   └── user_service.py      # 用户服务类
├── examples/
│   └── user_examples.py     # 使用示例
└── scripts/
    └── create_db_and_tables.py  # 数据库表创建
```

## 数据库表结构

```sql
CREATE TABLE users (
    user_id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE,
    wallet_address VARCHAR UNIQUE,
    invitation_code VARCHAR,
    verification_code VARCHAR,
    code_generated_at TIMESTAMP,
    code_expires_at TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

## 约束和验证

1. **必须有认证方式**: 用户必须至少有邮箱或钱包地址之一
2. **唯一性约束**: 每个邮箱和钱包地址只能属于一个用户
3. **邮箱验证**: 邮箱用户必须验证后才能登录
4. **钱包即用**: 钱包地址可以直接登录，无需验证
5. **用户状态**: 停用用户无法登录

这个设计简化了用户管理，提供了更好的用户体验，同时保持了数据的一致性和安全性。
