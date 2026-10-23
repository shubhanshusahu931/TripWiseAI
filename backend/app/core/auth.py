import httpx
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from app.core.config import settings

security = HTTPBearer(auto_error=False)

class CurrentUser(BaseModel):
    id: str
    email: str
    role: str = "authenticated"

DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"
DEMO_USER_EMAIL = "demo@tripwise.ai"

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> CurrentUser:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header or token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials.strip()

    # 1. Demo Mode or Local Test Token
    if token in ("demo-token", "test-token") or token.startswith("demo-"):
        return CurrentUser(id=DEMO_USER_ID, email=DEMO_USER_EMAIL, role="authenticated")

    # 2. Supabase JWT Verification with Secret
    if settings.SUPABASE_JWT_SECRET:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
                options={"verify_aud": False}  # Supabase tokens vary in audience config
            )
            user_id = payload.get("sub")
            email = payload.get("email", "")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload: missing sub",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return CurrentUser(id=str(user_id), email=email, role=payload.get("role", "authenticated"))
        except JWTError as e:
            # If secret check fails, let's try Supabase Auth API if URL is provided
            pass

    # 3. Supabase Auth API Verification (Fallback when secret is not configured or asymmetric)
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": settings.SUPABASE_KEY
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    return CurrentUser(
                        id=data.get("id"),
                        email=data.get("email", ""),
                        role=data.get("role", "authenticated")
                    )
        except Exception:
            pass

    # 4. Development mode unverified JWT decode (graceful fallback if Supabase secret not set locally)
    if settings.ENVIRONMENT == "development":
        try:
            unverified_claims = jwt.get_unverified_claims(token)
            user_id = unverified_claims.get("sub") or unverified_claims.get("id")
            if user_id:
                return CurrentUser(
                    id=str(user_id),
                    email=unverified_claims.get("email", "dev@tripwise.ai"),
                    role=unverified_claims.get("role", "authenticated")
                )
        except Exception:
            pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
