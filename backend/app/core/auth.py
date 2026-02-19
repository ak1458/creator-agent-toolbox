from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
settings = get_settings()
SECRET_KEY = getattr(settings, "secret_key", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode a JWT token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("token_decode_failed", error=str(e))
        return None


def get_user_id_from_token(token: str) -> str | None:
    """Extract user_id from a JWT token."""
    payload = decode_token(token)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    return user_id


# Simple in-memory user store for Phase 7
# In production, this should be a database table
# Format: {user_id: {"password_hash": str, "email": str}}
_USERS: dict[str, dict] = {}


def create_user(email: str, password: str) -> str:
    """Create a new user. Returns user_id."""
    import uuid
    
    user_id = str(uuid.uuid4())
    password_hash = get_password_hash(password)
    
    _USERS[user_id] = {
        "email": email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    logger.info("user_created", user_id=user_id, email=email)
    return user_id


def authenticate_user(email: str, password: str) -> str | None:
    """Authenticate a user by email/password. Returns user_id if valid."""
    # Find user by email
    for user_id, user_data in _USERS.items():
        if user_data["email"] == email:
            if verify_password(password, user_data["password_hash"]):
                return user_id
            else:
                return None
    
    return None


def get_user_by_id(user_id: str) -> dict | None:
    """Get user data by ID."""
    return _USERS.get(user_id)


# Demo users for testing
if not _USERS:
    # Create a demo user
    demo_user_id = create_user("demo@example.com", "demo123")
    logger.info("demo_user_created", user_id=demo_user_id)
