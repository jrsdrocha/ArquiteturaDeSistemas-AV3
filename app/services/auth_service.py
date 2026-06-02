import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository
from app.schemas.auth import AuthResponse


class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        self.token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    def register(self, username: str, password: str) -> AuthResponse:
        if self.user_repository.get_by_username(username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already registered",
            )

        user = self.user_repository.create(
            username=username,
            password=self.get_password_hash(password),
        )
        return AuthResponse(access_token=self.create_access_token(user.id, user.username))

    def login(self, username: str, password: str) -> AuthResponse:
        user = self.user_repository.get_by_username(username)
        if not user or not self.verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if user.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        return AuthResponse(access_token=self.create_access_token(user.id, user.username))

    def register_user(self, username: str, password: str) -> AuthResponse:
        return self.register(username, password)

    def login_user(self, username: str, password: str) -> AuthResponse:
        return self.login(username, password)

    def get_password_hash(self, password: str) -> str:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
        return f"pbkdf2_sha256${salt}${digest.hex()}"

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            algorithm, salt, expected_hash = hashed_password.split("$", 2)
        except ValueError:
            return False

        if algorithm != "pbkdf2_sha256":
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode(),
            salt.encode(),
            100_000,
        ).hex()
        return hmac.compare_digest(digest, expected_hash)

    def create_access_token(self, user_id: int, username: str) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "username": username,
            "exp": int(expires_at.timestamp()),
        }
        return self._encode_token(payload)

    def verify_access_token(self, token: str) -> dict[str, Any]:
        payload = self._decode_token(token)
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        return payload

    def _encode_token(self, payload: dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = self._b64encode(header)
        payload_b64 = self._b64encode(payload)
        signature = self._sign(f"{header_b64}.{payload_b64}")
        return f"{header_b64}.{payload_b64}.{signature}"

    def _decode_token(self, token: str) -> dict[str, Any]:
        try:
            header_b64, payload_b64, signature = token.split(".")
        except ValueError as exc:
            raise self._invalid_token_exception() from exc

        expected_signature = self._sign(f"{header_b64}.{payload_b64}")
        if not hmac.compare_digest(signature, expected_signature):
            raise self._invalid_token_exception()

        try:
            decoded = base64.urlsafe_b64decode(self._pad_b64(payload_b64))
            return json.loads(decoded)
        except (ValueError, json.JSONDecodeError) as exc:
            raise self._invalid_token_exception() from exc

    def _sign(self, value: str) -> str:
        digest = hmac.new(
            self.secret_key.encode(),
            value.encode(),
            hashlib.sha256,
        ).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    @staticmethod
    def _b64encode(data: dict[str, Any]) -> str:
        raw = json.dumps(data, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @staticmethod
    def _pad_b64(value: str) -> bytes:
        return (value + "=" * (-len(value) % 4)).encode()

    @staticmethod
    def _invalid_token_exception() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
