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
        clients_sql = conn.execute(
            """
            SELECT 
                c.id id,
                c.fio fio,
                c.money money,
                c.town town,
                a.name name
            FROM Client c
            JOIN Agency a ON a.id = c.agency
            """
        ).fetchall()

        clients = [dict(client) for client in clients_sql]

    with get_db_connection() as conn:
        agency_sql = conn.execute(
            """
            SELECT * FROM Agency
            """
        ).fetchall()

        agency = [dict(agency) for agency in agency_sql]

    context = {
        'request': request,
        'clients': clients,
        'agencies': agency,
    }

    return templates.TemplateResponse("clients.html", context)


@app.post('/clients/{client_id}/delete', response_class=RedirectResponse)
async def delete_system(request: Request, client_id: int):
    """Удаление системы"""
    with get_db_connection() as conn:
        conn.execute(
            '''
            delete from Client where id = ?
            ''',
            (client_id,)
        )

        conn.commit()

    return RedirectResponse('/clients', status_code=303)


@app.post("/clients", response_class=RedirectResponse)
async def create_client(
        fio: str = Form(...),
        money: int = Form(...),
        town: str = Form(...),
        agency: str = Form(...),
    ):

    with get_db_connection() as conn:
        conn.execute(
            '''
            insert into Client (fio, money, town, agency)
            values (?, ?, ?, ?)
            ''',
            (fio, money, town, agency)
        )

        conn.commit()

    return RedirectResponse('/clients', status_code=303)


@app.get("/estates", response_class=HTMLResponse)
async def estates(request: Request):
    """Получение списка всех систем"""
    with get_db_connection() as conn:
        estates_sql = conn.execute(
            """
                SELECT 
                    e.id id,
                    a.name agency,
                    e.name name,
                    e.address address,
                    e.square square,
                    e.rooms_cnt rooms_cnt,
                    e.posted_at posted_at,
                    etype.name type
                FROM Estate e
                JOIN Agency a ON a.id = e.agency
                JOIN EstateType etype ON etype.id = e.type
            """
        ).fetchall()

        estates = [dict(estate) for estate in estates_sql]

    with get_db_connection() as conn:
        agency_sql = conn.execute(
            """
            SELECT * FROM Agency
            """
        ).fetchall()

        agency = [dict(agency) for agency in agency_sql]

    with get_db_connection() as conn:
        estates_sql = conn.execute(
            """
            SELECT 
                *
            FROM EstateType e
            """
        ).fetchall()

        types = [dict(estate_type) for estate_type in estates_sql]

    context = {
        'request': request,
        'estates': estates,
        'agencies': agency,
        'types': types,
    }

    return templates.TemplateResponse("estates.html", context)


@app.post("/estates", response_class=RedirectResponse)
async def create_client(
        name: str = Form(...),
        address: str = Form(...),
        square: int = Form(...),
        agency: int = Form(...),
        type: int = Form(...),
        rooms_cnt: int = Form(...),
    ):

    with get_db_connection() as conn:
        conn.execute(
            '''
            insert into Estate (name, address, agency, square, type, rooms_cnt)
            values (?, ?, ?, ?, ?, ?)
            ''',
            (name, address, agency, square, type, rooms_cnt)
        )

        conn.commit()

    return RedirectResponse('/estates', status_code=303)


@app.post('/estates/{estate_id}/delete', response_class=RedirectResponse)
async def delete_estate(request: Request, estate_id: int):
    """Удаление системы"""
    with get_db_connection() as conn:
        conn.execute(
            '''
            delete from Estate where id = ?
            ''',
            (estate_id,)
        )

        conn.commit()

    return RedirectResponse('/estates', status_code=303)


@app.post("/estatetypes/", response_class=RedirectResponse)
async def create_client(
        name: str = Form(...),
    ):

    with get_db_connection() as conn:
        conn.execute(
            '''
            insert into EstateType (name)
            values (?)
            ''',
            (name, )
        )

        conn.commit()

    return RedirectResponse('/estates', status_code=303)


@app.get("/estates/xml")
def download_xml():
    """Получение данных в формате XML"""
    with get_db_connection() as conn:
        data_sql = conn.execute(
            '''
                SELECT 
                    e.id id,
                    a.name agency,
                    e.name name,
                    e.address address,
                    e.square square,
                    e.rooms_cnt rooms_cnt,
                    e.posted_at posted_at,
                    etype.name type
                FROM Estate e
                JOIN Agency a ON a.id = e.agency
                JOIN EstateType etype ON etype.id = e.type
            '''
        ).fetchall()
        data = [dict(data) for data in data_sql]

    xml_root = XML.Element("items")

    for raw in data:
        item_el = XML.SubElement(xml_root, "item")
        for key, value in raw.items():
            XML.SubElement(item_el, key).text = str(value)

    xml_data = XML.tostring(xml_root, encoding="utf-8")
    return Response(content=xml_data, media_type='application/xml')


@app.post("/xml/estates/upload")
def upload_xml(file: UploadFile = File(...)):
    """Загрузка и сохранение в таблицу данных о системах из XML"""
    contents = file.file.read()
    tree = XML.parse(BytesIO(contents))
    root_node = tree.getroot()

    with get_db_connection() as conn:
        for item in root_node.findall("item"):
            name = item.find("name").text
            diameter = item.find("diameter").text
            age = item.find("age").text
            galaxy = item.find("galaxy").text
            description = item.find("description").text

            conn.execute(
                '''
                INSERT INTO systems (name, diameter, age, galaxy, description)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (name, diameter, age, galaxy, description)
            )

            conn.commit()

    return {"message": "Success"}
