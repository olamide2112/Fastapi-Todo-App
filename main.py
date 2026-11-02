from fastapi import FastAPI, Request, status
from fastapi.openapi.docs import get_swagger_ui_html

from .models import Base

from .database import engine

from .routers import auth, todos,admin, users
# from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.responses import RedirectResponse 

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(docs_url=None)

Base.metadata.create_all(bind=engine)

# templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

@app.get("/")
def test(request: Request):
    # return templates.TemplateResponse(
    #     request=request, 
    #     name="home.html", 
    #     context={"request": request}
    # )
    return RedirectResponse(url="/todos/todo-page", status_code= status.HTTP_302_FOUND)


@app.get("/healthy")
async def healthy():
    return {"message": "Healthy"}


app.include_router(auth.router)

app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Todo App - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )
