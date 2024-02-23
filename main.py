from fastapi import FastAPI, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import List, Annotated
from database import SessionLocal
import database
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


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
origins = ['*']

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

@app.get("/world", response_class=HTMLResponse)
async def world():
    return """
        <title>...world</title>
        <h1>...world</h1>
    """
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BoardGameVault</title>
    <!-- Include HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body>
    <button hx-get="http://127.0.0.1:8000/" hx-swap="afterend">Click</button>
    <button hx-get="http://127.0.0.1:8000/items/412199" hx-swap="afterend">Click</button>
<tr id="replaceMe">
  <td colspan="3">
    <button class='btn' hx-get="http://127.0.0.1:8000/items/412199"
                        hx-target="#replaceMe"
                        hx-swap="afterend">
         Load More Agents... <img class="htmx-indicator" src="">
    </button>
  </td>
</tr>
</body>
</html>
    """


@app.get("/items/all", response_model=list[Boardgame_pydantic], response_model_exclude_unset=True)
async def read_items(db: db_dependency, skip: int = 0, limit: int = 10):
    items = db.query(database.Boardgame).offset(skip).limit(limit).all()
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


@app.get("/items/{id}", response_model=Boardgame_pydantic, response_model_exclude_unset=True)
async def read_items(id: int, db: db_dependency):
    items = db.query(database.Boardgame).filter(database.Boardgame.c.item_id == id).first()
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items


@app.patch("/items/{id}", response_model=Boardgame_pydantic, response_model_exclude_unset=True)
async def update_item(id: int, db: db_dependency):
    item = db.query(database.Boardgame).filter(database.Boardgame.c.item_id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.owned = not item.owned
    db.commit()
    return item
