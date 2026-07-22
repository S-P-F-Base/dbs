from fastapi import APIRouter, HTTPException  # noqa: F401
from pydantic import BaseModel

router = APIRouter()


class UserLogin(BaseModel):
    login: str
    password: str


@router.post("/dbs/register")
def register(user: UserLogin):
    return {"status": "ok", user.login: user.password}


@router.post("/dbs/login")
def login(user: UserLogin):
    return {"status": "ok", user.login: user.password}
