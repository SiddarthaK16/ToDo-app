from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter
from typing import Annotated
from sqlalchemy.orm import Session
from database import  SessionLocal
from models import Todos
from starlette import status
from pydantic import   BaseModel, Field
from .auth import get_current_user



router = APIRouter()



def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session,Depends(get_db)]
user_dependency= Annotated[dict,Depends(get_current_user)]

class ToDoRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5, max_length=100)
    complete: bool = Field(default=False)
    priority: int = Field(..., ge=1, le=10)


    model_config = {
        "json_schema_extra":{
            "example":{
                "title": "Your ToDo task",
                "description": "Define the task and its outcome in short sentence!",
                "complete": False,
                "priority": 2,
            }
        }
    }                 #will show in example whatever we write here



@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,
                   db: db_dependency):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return db.query(Todos).filter(Todos.owner_id==user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,
                    db: db_dependency,todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    todo_model= db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()  # .first() to save and enhance performance
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                      db: db_dependency, todo_request: ToDoRequest):

    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    todo_model=Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)  #to telling db we are going to add smt into db
    db.commit()

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency,
                      todo_request: ToDoRequest,
                      todo_id: int = Path(gt=0) ,
                      ):
    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    todo_model= db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="ToDo not found")

    todo_model.title= todo_request.title
    todo_model.description= todo_request.description
    todo_model.complete= todo_request.complete
    todo_model.priority= todo_request.priority

    db.add(todo_model)
    db.commit()

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)  ):

    if user is None:
        raise HTTPException(status_code=400, detail="User not found")

    todo_model= db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="ToDo not found")
    db.delete(todo_model)
    db.commit()


