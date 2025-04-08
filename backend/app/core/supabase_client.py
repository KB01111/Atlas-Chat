import os
from supabase import create_client, Client
from fastapi import HTTPException, status
import jwt

_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not _SUPABASE_URL or not _SUPABASE_KEY:
    raise RuntimeError("Supabase credentials are not set in environment variables.")

supabase: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)

def verify_supabase_jwt(token: str) -> dict:
    """
    Verify a Supabase JWT token and return its payload.
    """
    try:
        # Supabase JWTs are signed with the project's JWT secret
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if not jwt_secret:
            raise RuntimeError("JWT_SECRET_KEY not set in environment variables.")
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")