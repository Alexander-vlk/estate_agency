from io import BytesIO

from fastapi import Request, FastAPI, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.staticfiles import StaticFiles
from xml.etree import ElementTree as XML

from utils import get_db_connection

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
