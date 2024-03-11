import uuid
from typing import Annotated, Generator

from fastapi import FastAPI, HTTPException, Depends, Request, Response, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import database
from models import BoardgamePydantic
from startup import check_db_connection, check_table_exists, new_data_job

# create FastAPI app
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

# Check database connection and table existence
check_db_connection(database.engine)
check_table_exists("boardgames", database.engine)


# Get new data from BGG API on startup
new_data_job()


# Dependency to get the database session
def get_db() -> Generator:
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


# Routes
@app.get("/")
async def home(request: Request) -> Response:
    """
    Renders the home page template with context data.

    Sets a session cookie if it doesn't already exist.

    Args:
        request: The incoming HTTP request object.

    Returns:
        An HTTP response with the rendered home page template.
    """
    session_key = request.cookies.get("session_key", uuid.uuid4().hex)
    context = {"request": request, "title": "BoardGameVault"}
    response = templates.TemplateResponse("home.html", context)
    response.set_cookie(key="session_key", value=session_key, expires=259200)  # 3 days
    return response


@app.get("/get_new_data")
async def start_new_data_job() -> None:
    """
    Triggers the background job to fetch new data from BGG API.

    Returns:
        None
    """
    new_data_job()


@app.post("/item", response_class=HTMLResponse)
async def get_item(
    request: Request, searched_id: Annotated[int, Form()], db: db_dependency
) -> Response:
    """
    Queries the database for a board game item based on the provided ID.
    Renders the item details template with the items data.
    Raises a 404 HTTP exception if the item is not found.

    Args:
        request: The incoming HTTP request object.
        searched_id: The ID of the board game item to retrieve.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item details template.
    """
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
    """
    Queries the database for a list of board game items.
    Filters items by type to get only boardgames and orders them by Bayes average descending.
    Renders the item list template with the fetched items data.
    Raises a 404 HTTP exception if no items are found.

    Args:
        request: The incoming HTTP request object.
        skip: The number of items to skip.
        limit: The number of items to retrieve.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item list template.
    """
    items = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.type == "boardgame")
        .order_by(database.Boardgame.c.bayes_average.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    context = {"request": request, "items": items}
    return templates.TemplateResponse("item_table.html", context)


@app.get("/search", response_class=HTMLResponse)
async def search_items(request: Request, search: str, db: db_dependency) -> Response:
    """
    Searches the database for board game items based on a search term.
    The items are filtered and ordered first by ownership then by name.
    Renders the item list template with the fetched items data.
    Raises a 404 HTTP exception if no items are found.

    Args:
        request: The incoming HTTP request object.
        search: The search term to use for filtering items.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item list template.
    """
    items = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.name != "-1")
        .order_by(database.Boardgame.c.owned.desc(), database.Boardgame.c.name)
        .filter(database.Boardgame.c.name.icontains(search))
        .limit(200)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    context = {"request": request, "items": items}
    return templates.TemplateResponse("item_table.html", context)


@app.get("/owned", response_class=HTMLResponse)
async def owned_items(request: Request, db: db_dependency) -> Response:
    """
    Queries the database for a list of owned board game items.
    Items are ordered alphabetically.
    Renders the item list template with the fetched items data.
    Raises a 404 HTTP exception if no owned items are found.

    Args:
        request: The incoming HTTP request object.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item list template.
    """
    items = (
        db.query(database.Boardgame)
        .order_by(database.Boardgame.c.name.asc())
        .filter(database.Boardgame.c.owned == True)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail="No owned items found")
    context = {"request": request, "items": items}
    return templates.TemplateResponse("item_table.html", context)


@app.patch("/item/update_owned/{updated_id}", response_model_exclude_unset=True)
async def update_item(updated_id: int, db: db_dependency) -> None:
    """
    Updates the "owned" status of the boardgame with the provided ID.
    The function first checks the current status and then switches it to the opposite.
    Raises a 404 HTTP exception if the item is not found.

    Args:
     updated_id: The ID of the board game to update.
     db: The database session dependency.

    Returns:
     None
    """
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    database.update_item_ownership(updated_id)


@app.post("/item/update_played/add/{updated_id}", response_model_exclude_unset=True)
async def update_item(request: Request, updated_id: int, db: db_dependency) -> Response:
    """
    Increments the "times played" count of the board game with the provided ID.
    The current date is added to the "dates played" list.
    After updating the count, re-fetches and re-renders the item from the database.
    Raises a 404 HTTP exception if the item is not found.

    Args:
        request: The incoming HTTP request object.
        updated_id: The ID of the board game to update.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item details template.
    """
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    database.update_times_played(updated_id, False)
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    context = {"request": request, "items": [item]}
    return templates.TemplateResponse("item.html", context)


@app.post("/item/update_played/subs/{updated_id}", response_model_exclude_unset=True)
async def update_item(request: Request, updated_id: int, db: db_dependency) -> Response:
    """
    Decrements the "times played" count of the board game with the provided ID.
    The last date is deleted from the "dates played" list.
    After updating the count, re-fetches and re-renders the item from the database.
    Raises a 404 HTTP exception if the item is not found.

    Args:
        request: The incoming HTTP request object.
        updated_id: The ID of the board game to update.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item details template.
    """
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    database.update_times_played(updated_id, True)
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    context = {"request": request, "items": [item]}
    return templates.TemplateResponse("item.html", context)


@app.post("/item/update_comments/{updated_id}", response_model_exclude_unset=True)
async def update_item(
    request: Request,
    comments: Annotated[str, Form()],
    updated_id: int,
    db: db_dependency,
) -> Response:
    """
    Rewrites the comments column for the board game with the provided ID.
    After updating the comments, re-fetches and re-renders the item from the database.
    Raises a 404 HTTP exception if the item is not found.

    Args:
        request: The incoming HTTP request object.
        comments: The new comments (received from the form).
        updated_id: The ID of the board game to update.
        db: The database session dependency.

    Returns:
        An HTTP response with the rendered item details template.
    """
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    database.update_comments(updated_id, comments)
    item = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == updated_id)
        .first()
    )
    context = {"request": request, "items": [item]}
    return templates.TemplateResponse("item.html", context)


# Raw data routes
@app.get(
    "/items/all",
    response_model=list[BoardgamePydantic],
    response_model_exclude_unset=True,
)
async def read_items(db: db_dependency, skip: int = 0, limit: int = 10):
    """
    Retrieves a list of board games from the database in JSON.
    Uses offset and limit parameters.
    Raises a 404 HTTP exception if no items are found.

    Args:
        db: The database session dependency.
        skip: The number of items to skip. Defaults to 0.
        limit: The number of items to retrieve. Defaults to 10.

    Returns:
        A list of BoardgamePydantic objects representing the retrieved items.
    """
    items = db.query(database.Boardgame).offset(skip).limit(limit).all()
    if not items:
        raise HTTPException(status_code=404, detail="Items not found")
    return items


@app.get(
    "/items/{searched_id}",
    response_model=BoardgamePydantic,
    response_model_exclude_unset=True,
)
async def read_items_id(searched_id: int, db: db_dependency):
    """
    Retrieves a single board game from the database by ID.
    Raises a 404 HTTP exception if the item with the provided ID is not found.

    Args:
        searched_id: The ID of the board game to retrieve.
        db: The database session dependency.

    Returns:
        A BoardgamePydantic object representing the retrieved item.
    """
    items = (
        db.query(database.Boardgame)
        .filter(database.Boardgame.c.item_id == searched_id)
        .first()
    )
    if not items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items
