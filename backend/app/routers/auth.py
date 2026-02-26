from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import auth as auth_schema
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.utils.database import get_db
from app.utils.utils import hash_password
from app.models import user as user_model
from app.utils import utils


router = APIRouter(
    tags=['Authentication'],
    prefix='/auth'
)

'''
####################################################
                    Sign up
####################################################
'''

@router.post(
        '/signup',
        response_model=auth_schema.SignupResponse,
        status_code=status.HTTP_201_CREATED
    )
def create_user(data: auth_schema.SignupCreate, db: Session = Depends(get_db)):    
    # check password and confirm password
    if data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Passwords do not match'
        )
    
    user_data = data.model_dump(exclude={'confirm_password'}) # exculde confirm password
    
    # hashed the password
    user_data['password'] = hash_password(user_data['password'])
    
    # add to db
    new_user = user_model.User(**user_data)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError as e:
        db.rollback() # rollback the session
        
        # check username is unique
        if 'uq_users_username' in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Username already exists'
            )
        
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Database constraint violation")
    
    return new_user



'''
####################################################
                    Login
####################################################
'''

@router.post('/login', response_model=auth_schema.LoginResponse)
def login_user(
        data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
    ):    
    
    # fetch the user
    user = db.query(user_model.User).filter(user_model.User.username == data.username).first()
    
    
    # check user existance
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password'
        )
    
    # check password
    checking_password = utils.validate_password(data.password, user.password)
    
    if not checking_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect username or password'
        )
    
    # create access token
    access_token = utils.create_access_token({'user_id': user.id})
    
    return {'access_type': 'bearer', 'access_token': access_token}