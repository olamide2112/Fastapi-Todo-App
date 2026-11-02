from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Path, APIRouter, Request, status
from pydantic import BaseModel, Field
from ..models import Todos
from ..database import  SessionLocal
from starlette import status
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path as FilePath

templates = Jinja2Templates(directory=str(FilePath(__file__).resolve().parent.parent / "templates"))

router = APIRouter(
    prefix = '/todos',
    tags = ['todos']

)


def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title : str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority : int= Field(gt=0,lt=6)
    completed : bool

def redirect_to_login():
    redirect_response =  RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response



###Pages
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()
        
        todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

        return templates.TemplateResponse(
            request, "todo.html", {"user": user, "todos": todos}
        )
    except:
        return redirect_to_login()

@router.get("/add-todo-page")
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        return templates.TemplateResponse(request, "add-todo.html", {"user": user})
    except Exception:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, db: db_dependency, todo_id: int = Path(gt=0)):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        todo = db.query(Todos).filter(
            Todos.id == todo_id,
            Todos.owner_id == user.get('id')
        ).first()
        if todo is None:
            raise HTTPException(status_code=404, detail='Todo not found')
        return templates.TemplateResponse(
            request, "edit-todo.html", {"user": user, "todo": todo}
        )
    except HTTPException:
        raise
    except Exception:
        return redirect_to_login()

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail= 'Authentication faild')
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code = status.HTTP_200_OK)
async def read_todo(user: user_dependency,db: db_dependency, todo_id: int = Path(gt= 0)):
    if user is None:
        raise HTTPException(status_code=401, detail= 'Authentication faild')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail= 'Todo not found.')

# Create New Todo
@router.post("/todo", status_code= status.HTTP_201_CREATED)
async def create_todo(user:user_dependency ,db: db_dependency, todo_request: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail= 'Authentication faild')
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

# Update Request Method
# Update Request Method
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, 
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401, detail= 'Authentication faild')
    
    # 1. Find the existing todo item
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    
    # 2. Check if it exists (Fixed 'details' to 'detail')
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
        
    # 3. Update the attributes
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    # 4. Save updates to database
    db.add(todo_model)
    db.commit()
    # No return statement needed here because HTTP 204 expects an empty response

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency ,db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail= 'Authentication failed')
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).delete()  # Use delete() method for direct deletion
    
    db.commit()


