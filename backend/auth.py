from datetime import timedelta, datetime, UTC
from typing import Annotated
from fastapi import FastAPI, APIRouter, Depends, HTTPException,Request
from jose import jwt
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware

from backend.database import SessionLocal
from backend.models import User
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()


router = APIRouter()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRY_TIME=os.getenv("ACCESS_TOKEN_EXPIRY_TIME")

class Check_User_Structure(BaseModel):
    name: str =Field(min_length=3)
    email: str =Field(min_length=10)
    password: str =Field(min_length=6)

class LoginSchema(BaseModel):
    email: str = Field(min_length=10)
    password: str = Field(min_length=6)

hash_Context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_the_password(password):
    return hash_Context.hash(password)
def verify_password(user_given_password,user_db_password):
    return hash_Context.verify(user_given_password,user_db_password)


def create_access_token(data:dict,expires_delta:timedelta=None):
    encode=data.copy()
    expiry=datetime.now(UTC)+(expires_delta or timedelta(minutes=60))
    encode.update({"exp":expiry})
    return jwt.encode(encode,SECRET_KEY,ALGORITHM)




def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

def get_the_current_user(req:Request):
    token=req.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401,detail="No token found")
    scheme,access_token=token.split()
    if scheme.lower()!="bearer":
        raise HTTPException(status_code=401,detail="Invalid authentication scheme")
    payload=jwt.decode(access_token,SECRET_KEY,algorithms=[ALGORITHM])
    print("payload",payload)
    return payload


user_dependency=Annotated[dict,Depends(get_the_current_user)]




@router.post("/auth/create-user", status_code=status.HTTP_201_CREATED)
async def create_user(user:Check_User_Structure,db:db_dependency):
    check_user_exist=db.query(User).filter(User.email==user.email).first()
    if check_user_exist is not None:
        raise HTTPException(status_code=400,detail="User already exists")
    hashed_password=hash_the_password(user.password)
    new_user=User(name=user.name,
                  email=user.email,
                  password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"user created successfully", "user": {"id": new_user.id, "email": new_user.email}}


@router.post("/auth/login", status_code=status.HTTP_200_OK)
async def user_login(user_data: LoginSchema, db: db_dependency):
    check_user_exist = db.query(User).filter(User.email == user_data.email).first()

    if check_user_exist is None:
        raise HTTPException(status_code=404, detail="User not found")

    isMatching = verify_password(user_data.password, check_user_exist.password)

    if not isMatching:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(check_user_exist.id)},
        expires_delta=timedelta(minutes=int(ACCESS_TOKEN_EXPIRY_TIME))
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": check_user_exist.id
    }
