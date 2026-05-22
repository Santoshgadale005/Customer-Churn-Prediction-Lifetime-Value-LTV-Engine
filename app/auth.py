from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt

router = APIRouter()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"])

users = {}

class User(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(user: User):

    hashed_password = pwd_context.hash(user.password)

    users[user.email] = hashed_password

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(user: User):

    stored_password = users.get(user.email)

    if not stored_password:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    if not pwd_context.verify(
        user.password,
        stored_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    token = jwt.encode(
        {"sub": user.email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token
    }