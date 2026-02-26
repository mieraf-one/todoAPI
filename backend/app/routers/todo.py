from fastapi import APIRouter, Depends
from app.utils.utils import get_current_user
from app.models import user as user_model

router = APIRouter(
    tags=['Todos'],
    prefix='/todos'
)


@router.post('/')
def create_todo(current_user: user_model.User = Depends(get_current_user)):
    return current_user