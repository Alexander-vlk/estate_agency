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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница"""
    with get_db_connection() as conn:
        agency_sql = conn.execute("SELECT * FROM Agency").fetchall()

        agency = [dict(agency) for agency in agency_sql]

    context = {
        'request': request,
        'agencies': agency,
    }
    return templates.TemplateResponse("index.html", context)


@app.get("/clients", response_class=HTMLResponse)
async def systems(request: Request):
    """Получение списка всех систем"""
    with get_db_connection() as conn:
        clients_sql = conn.execute("SELECT * FROM Client").fetchall()

        clients = [dict(client) for client in clients_sql]

    context = {
        'request': request,
        'clients': clients,
    }

    return templates.TemplateResponse("clients.html", context)


@app.post("/clients", response_class=RedirectResponse)
async def create_client(
        fio: str = Form(...),
        money: float = Form(...),
        town: int = Form(...),
        agency: str = Form(...),
    ):

    with get_db_connection() as conn:
        conn.execute(
            '''
            insert into systems (name, diameter, age, galaxy)
            values (?, ?, ?, ?)
            ''',
            (fio, money, town, agency)
        )

        conn.commit()

    return RedirectResponse('/clients', status_code=303)


@app.get("/estates", response_class=HTMLResponse)
async def systems(request: Request):
    """Получение списка всех систем"""
    with get_db_connection() as conn:
        estates_sql = conn.execute("SELECT * FROM Estate").fetchall()

        estates = [dict(estate) for estate in estates_sql]

    context = {
        'request': request,
        'estates': estates,
    }

    return templates.TemplateResponse("estates.html", context)
