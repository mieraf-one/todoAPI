from fastapi import APIRouter, Depends, status, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.utils.utils import get_current_user
from app.models import user as user_model, todo as todo_model
from app.schemas import todo as todo_schema
from app.utils.database import get_db
from typing import List

router = APIRouter(
    tags=['Todos'],
    prefix='/todos'
)


@router.post('', response_model=todo_schema.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
        data: todo_schema.TodoCreate,
        db: Session = Depends(get_db),
        current_user: user_model.User = Depends(get_current_user)
    ):
    
    user_data = data.model_dump()
    user_data['owner_id'] = current_user.id
    
    new_todo = todo_model.Todo(**user_data)
    
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    return todo_schema.TodoResponse(
                id=new_todo.id,
                owner_username=current_user.username,
                title=new_todo.title,
                content=new_todo.content,
                is_done=new_todo.is_done,
                created_at=new_todo.created_at
            )


@router.get('', response_model=List[todo_schema.TodoResponse])
def get_todos(
        is_done: bool = Query(None),
        sort_by: str | None = Query('created_at'),
        sort_order: str | None = Query('desc'),
        current_user: user_model.User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    
    todos = (
        db.query(todo_model.Todo)
            .filter(todo_model.Todo.owner_id == current_user.id)
    )
    
    if sort_by in ['created_at', 'title', 'is_done']:
        column = getattr(todo_model.Todo, sort_by)
        
        if sort_order == 'desc':
            column = column.desc()
        elif sort_by == 'asc':
            column = column.asc()
        
        todos = todos.order_by(column)
        
    
    return [
        todo_schema.TodoResponse(
            id=todo.id,
            owner_username=current_user.username,
            title=todo.title,
            content=todo.content,
            is_done=todo.is_done,
            created_at=todo.created_at
        )
        
        for todo in todos
    ]

@router.get('/{id}', response_model=todo_schema.TodoResponse)
def get_todo(
        id: int,
        current_user: Session = Depends(get_current_user)
    ):
    
    todos = current_user.todos
    
    for todo in todos:
        if todo.id == id:
            return todo_schema.TodoResponse(
                id=todo.id,
                owner_username=current_user.username,
                title=todo.title,
                content=todo.content,
                is_done=todo.is_done,
                created_at=todo.created_at
            )
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Todo not found'
    )
    


@router.patch('/{id}', response_model=todo_schema.TodoResponse)
def get_todo(
        id: int,
        data: todo_schema.TodoUpdate,
        current_user: Session = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):

    todo = (
        db.query(todo_model.Todo)
            .filter(
                todo_model.Todo.id == id,
                todo_model.Todo.owner_id == current_user.id)
            .first()
    )
    
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found'
        )
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)
    
    db.commit()
    db.refresh(todo)
    
    return todo_schema.TodoResponse(
            id=todo.id,
            owner_username=current_user.username,
            title=todo.title,
            content=todo.content,
            is_done=todo.is_done,
            created_at=todo.created_at
        )
    
    
@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def get_todo(
        id: int,
        current_user: Session = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):    

    todo = (
        db.query(todo_model.Todo)
            .filter(
                todo_model.Todo.id == id,
                todo_model.Todo.owner_id == current_user.id)
    )
    
    if todo.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Todo not found'
        )
    
    todo.delete()
    db.commit()