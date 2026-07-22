import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import DataBase

router = APIRouter()


class UserLogin(BaseModel):
    login: str
    password: str = Field(..., min_length=8)


class UserChangePassword(BaseModel):
    login: str
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


def _password_sha256(password: str) -> bytes:
    return hashlib.sha256(password.encode("utf-8")).digest()


def _create_token(login: str) -> str:
    profile = DataBase.profiles.find_one(login=login)
    assert profile, "Never"

    token = secrets.token_hex(32).upper()
    expires = datetime.now(UTC) + timedelta(days=30)
    DataBase.sessions.insert(
        {
            "token": token,
            "user_id": profile["user_id"],
            "expires_at": expires.isoformat(),
        }
    )
    return token


@router.post("/api/dbs/auth/register")
def register(user: UserLogin):
    if DataBase.profiles.find_one(login=user.login):
        raise HTTPException(status_code=400, detail="Login collision")

    password_hash = bcrypt.hashpw(_password_sha256(user.password), bcrypt.gensalt())
    DataBase.profiles.insert({"login": user.login, "password_hash": password_hash})
    return {"status": "ok", "token": _create_token(user.login)}


@router.post("/api/dbs/auth/login")
def login(user: UserLogin):
    profile = DataBase.profiles.find_one(login=user.login)
    if not profile:
        raise HTTPException(status_code=403, detail="Invalid login or password")

    if not bcrypt.checkpw(_password_sha256(user.password), profile["password_hash"]):
        raise HTTPException(status_code=403, detail="Invalid login or password")

    return {"status": "ok", "token": _create_token(user.login)}


@router.post("/api/dbs/auth/change_password")
def change_password(user: UserChangePassword):
    profile = DataBase.profiles.find_one(login=user.login)
    if not profile:
        raise HTTPException(status_code=403, detail="Invalid login or password")

    if not bcrypt.checkpw(
        _password_sha256(user.old_password),
        profile["password_hash"],
    ):
        raise HTTPException(status_code=403, detail="Invalid login or password")

    password_hash = bcrypt.hashpw(_password_sha256(user.new_password), bcrypt.gensalt())
    DataBase.profiles.upsert(
        {"login": user.login, "password_hash": password_hash},
        ["login"],
    )
    return {"status": "ok"}
