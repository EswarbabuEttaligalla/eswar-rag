from __future__ import annotations

from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.models.token import RefreshToken
from app.models.user import User
from app.repositories.token_repo import RefreshTokenRepository
from app.repositories.user_repo import UserRepository
from app.utils.security import hash_token


class AuthService:
    def __init__(self, session):
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)

    async def register(self, email: str, password: str, full_name: str | None = None) -> User:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User inactive")
        access_token = create_access_token(str(user.id), user.role)
        refresh_token = create_refresh_token(str(user.id))
        await self._store_refresh_token(user.id, refresh_token)
        return access_token, refresh_token

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        token_hash = hash_token(refresh_token)
        token = await self.token_repo.get_by_hash(token_hash)
        if not token or token.revoked:
            raise HTTPException(status_code=401, detail="Refresh token revoked")
        if str(token.user_id) != str(payload.get("sub")):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token expired")
        await self.token_repo.revoke(token)
        user = await self.user_repo.get(token.user_id)
        role = user.role if user else "user"
        access_token = create_access_token(str(token.user_id), role)
        new_refresh = create_refresh_token(str(token.user_id))
        await self._store_refresh_token(token.user_id, new_refresh)
        return access_token, new_refresh

    async def logout(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token)
        token = await self.token_repo.get_by_hash(token_hash)
        if token:
            await self.token_repo.revoke(token)

    async def _store_refresh_token(self, user_id, refresh_token: str) -> None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token = RefreshToken(user_id=user_id, token_hash=hash_token(refresh_token), expires_at=expires_at)
        await self.token_repo.create(token)
