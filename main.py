from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Annotated
from database import engine, SessionLocal
import database
from sqlalchemy.orm import Session


class item(BaseModel):
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/items/all", response_model=list[item], response_model_exclude_unset=True)
async def read_items(db: db_dependency):
    items = db.query(database.Boardgame).limit(10).all()
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    print(type(items))
    return items


@app.get("/items/{id}", response_model=item, response_model_exclude_unset=True)
async def read_items(id: int, db: db_dependency):
    items = db.query(database.Boardgame).filter(database.Boardgame.item_id == id).first()
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items
# async def read_items(skip: int = 0, limit: int = 10, db: Session = db_dependency, response_model=database.Boardgame) -> Response:
#    items = db.query(database.Boardgame).offset(skip).limit(limit).all()
