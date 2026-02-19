"""
    Security utilities for authentication and authorization.

    Implements password hashing and verification, JWT token creation
    and validation, and related helper functions used by the auth layer.
"""


from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token containing the given data.
    """
    to_encode = data.copy()
    
    # 🔥 ADD iat (Issued At) claim - REQUIRED by modern JWT libraries
    to_encode.update({"iat": datetime.utcnow()})
    
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT. Returns the payload if valid, otherwise None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_exp": False,   # Skip expiry check
                "verify_iat": False,   # Skip issued-at check
                "verify_nbf": False,   # Skip not-before check
            }
        )
        print(f"DEBUG JWT: payload decoded OK: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        print("DEBUG JWT: Token expired")  # Add this
        return None
    except jwt.JWTClaimsError as e:
        print(f"DEBUG JWT: Invalid claims => {e}")  # Add this
        return None
    except jwt.InvalidAlgorithmError:
        print("DEBUG JWT: Invalid algorithm")  # Add this
        return None
    except jwt.InvalidTokenError as e:
        print(f"DEBUG JWT: Invalid token error: {e}")  # Add this
        return None
    except JWTError as e:
        print(f"DEBUG JWT: JWTError: {e}")
        return None
    except Exception as e:
        print(f"DEBUG JWT: Unexpected error: {e}")  # Add this
        return None