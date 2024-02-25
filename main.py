from fastapi import FastAPI, HTTPException, Depends, Response, Form
from pydantic import BaseModel
from typing import List, Annotated
from database import SessionLocal
import database
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import templates


class Boardgame_pydantic(BaseModel):
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
#
# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.post("/item", response_class=HTMLResponse)
async def root(id: Annotated[int, Form()], db: db_dependency):
    item = (
        db.query(database.Boardgame).filter(database.Boardgame.c.item_id == id).first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    response = templates.item_header() + templates.item(item)
    return response


# @app.post("/items", response_model=HTMLResponse)
# async def read_items(db: db_dependency, skip: Annotated[int, Form()], limit: Annotated[int, Form()]):
#     items = db.query(database.Boardgame).offset(skip).limit(limit).all()
#     if not items:
#         raise HTTPException(status_code=404, detail="Items not found")
#     response = templates.item_header()
#     for item in items:
#         response += templates.item(item)
#     return response


@app.post("/items", response_class=HTMLResponse)
async def read_items(
    skip: Annotated[int, Form()], limit: Annotated[int, Form()], db: db_dependency
):
    items = (
        db.query(database.Boardgame)
        .order_by(database.Boardgame.c.bayes_average.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    response = templates.item_header()
    for item in items:
        response += templates.item(item)
    return response


@app.get(
    "/items/all",
    response_model=list[Boardgame_pydantic],
    response_model_exclude_unset=True,
)
async def read_items(db: db_dependency, skip: int = 0, limit: int = 10):
    items = db.query(database.Boardgame).offset(skip).limit(limit).all()
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


@app.get(
    "/items/{id}", response_model=Boardgame_pydantic, response_model_exclude_unset=True
)
async def read_items(id: int, db: db_dependency):
    items = (
        db.query(database.Boardgame).filter(database.Boardgame.c.item_id == id).first()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items


@app.patch(
    "/items/{id}", response_model=Boardgame_pydantic, response_model_exclude_unset=True
)
async def update_item(id: int, db: db_dependency):
    item = (
        db.query(database.Boardgame).filter(database.Boardgame.c.item_id == id).first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.owned = not item.owned
    db.commit()
    return item
