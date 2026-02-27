from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import os
import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

from app.utils.database import get_db
from app.models import user as user_model, token as token_model

# load env
load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')

oauth2scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


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


def create_refresh_token(data: dict, db: Session):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=5)
    token_type = 'refresh'
    
    to_encode.update({'exp': expire, 'type': token_type})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    save_to_db = token_model.Token(token=encoded_jwt, user_id=to_encode['user_id'])
    
    db.add(save_to_db)
    db.commit()
    
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


def refresh_token(token: str, db: Session) -> str | HTTPException:
    try:
        payload: dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # check the token is refresh
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid refresh token "type"'
            )
        
        # fetch the user by payload username
        user_id = payload.get('user_id')
        user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
        
        # check user existance
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid refresh token "user not found"'
            )
        
        # fetch token from db
        db_token = db.query(token_model.Token).filter(token_model.Token.token == token).first()
        
        if db_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid Refresh token'
            )
        
    except jwt.ExpiredSignatureError:
        # fetch token from db
        db_token = db.query(token_model.Token).filter(token_model.Token.token == token).first()
        
        # check the token exists in db and if there check also owner is itself
        if db_token is not None:
            db.delete(db_token)
            db.commit()  # delete the expired token
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='refresh token Expired'
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token "all error"'
        )
    
    # create new access token
    create_new_access_token  = create_access_token({'user_id': user_id})
    
    return create_new_access_token
