from fastapi import FastAPI, Depends, HTTPException, Path
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models
from models import Todos
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency= Annotated[Session,Depends(get_db)]

@app.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency,todo_id: int = Path(gt=0)):
    todo_model= db.query(Todos).filter(Todos.id == todo_id).first()  # .first() to save and enhance performance
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")

