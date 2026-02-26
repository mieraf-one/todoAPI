import jwt
import os
from dotenv import load_dotenv
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import user as user_model
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


oauth2scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
print(f'hello + {ACCESS_TOKEN_EXPIRE_MINUTES}')


def hash_password(password: str):
    password_hash = PasswordHash.recommended()
    hashed_password = password_hash.hash(password=password)
    
    return hashed_password


def validate_password(plain_password: str, hashed_password: str):
    password_hash = PasswordHash.recommended()
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    token_type = 'access'
    
    to_encode.update({'exp': expire, 'type': token_type})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
        token: str = Depends(oauth2scheme),
        db: Session = Depends(get_db)
    ):
    try:
        # decode token
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('user_id')
        
        # check the token is refresh
        if payload.get('type') != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
        
        # check user_id existance
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired'
            )
        
    except jwt.PyJWTError:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )
    
    # fetch user object
    user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    
    # check user existance
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )
    
    return user