from fastapi import FastAPI, HTTPException, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Annotated, Generator
import uuid
import database


class BoardgamePydantic(BaseModel):
    __tablename__ = "boardgames"

    item_id: int
    type: str
    name: str
    owned: bool
    alternate_names: str
    description: str
    yearpublished: int
    minplayers: int
    maxplayers: int
    playingtime: int
    minplaytime: int
    maxplaytime: int
    age: int
    categories: str
    mechanics: str
    families: str
    integrations: str
    implementations: str
    designers: str
    artists: str
    publishers: str
    users_rated: int
    average_rating: float
    bayes_average: float
    bgg_rank: int
    num_weights: int
    average_weight: float
    thumbnail: str
    image: str


app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def home(request: Request) -> Response:
    session_key = request.cookies.get("session_key", uuid.uuid4().hex)
    context = {"request": request, "title": "Home"}
    response = templates.TemplateResponse("home.html", context)
    response.set_cookie(key="session_key", value=session_key, expires=259200)  # 3 days
    return response


@app.post("/item", response_class=HTMLResponse)
async def get_item(
    request: Request, searched_id: Annotated[int, Form()], db: db_dependency
) -> Response:
    session_key = request.cookies.get("session_key")
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == searched_id)
        .first()
    )
    context = {"request": request, "items": [item]}
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse("item.html", context)


@app.post("/items", response_class=HTMLResponse)
async def read_items(
    request: Request,
    skip: Annotated[int, Form()],
    limit: Annotated[int, Form()],
    db: db_dependency,
) -> Response:
    items = (
        db.query(database.Boardgame)
        .order_by(database.Boardgame.c.bayes_average.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    context = {"request": request, "items": items}
    return templates.TemplateResponse("item.html", context)


@app.get("/search", response_class=HTMLResponse)
async def search_items(request: Request, search: str, db: db_dependency):
    items = (
        db.query(database.Boardgame)
        .order_by(database.Boardgame.c.bayes_average.desc())
        .filter(database.Boardgame.c.name.icontains(search))
        .limit(200)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    context = {"request": request, "items": items}
    return templates.TemplateResponse("item.html", context)


@app.get("/owned", response_class=HTMLResponse)
async def owned_items(request: Request, db: db_dependency):
    items = (
        db.query(database.Boardgame)
        .order_by(database.Boardgame.c.name.desc())
        .filter(database.Boardgame.c.owned == True)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="No owned items found")
    context = {"request": request, "items": items}
    return templates.TemplateResponse("item.html", context)


@app.patch("/items/update/{updated_id}", response_model_exclude_unset=True)
async def update_item(updated_id: int, db: db_dependency):
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    database.update_item_ownership(updated_id)


# Raw data endpoints


@app.get(
    "/items/all",
    response_model=list[BoardgamePydantic],
    response_model_exclude_unset=True,
)
async def read_items(db: db_dependency, skip: int = 0, limit: int = 10):
    items = db.query(database.Boardgame).offset(skip).limit(limit).all()
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


@app.get(
    "/items/{searched_id}",
    response_model=BoardgamePydantic,
    response_model_exclude_unset=True,
)
async def read_items(searched_id: int, db: db_dependency):
    items = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == searched_id)
        .first()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items
