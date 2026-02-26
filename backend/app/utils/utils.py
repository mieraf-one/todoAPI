import jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import user as user_model
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta, timezone


SECRET_KEY = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e9'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2scheme = OAuth2PasswordBearer(tokenUrl='login')



def hash_password(password: str):
    password_hash = PasswordHash.recommended()
    hashed_password = password_hash.hash(password=password)
    
    return hashed_password


def validate_password(plain_password: str, hashed_password: str):
    password_hash = PasswordHash.recommended()
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    user = db.query(user_model.User).filter(user_model.User.user_id == user_id).first()
    
    # check user existance
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found'
        )
    
    return user