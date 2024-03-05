from sqlalchemy import create_engine, MetaData, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, select
from datetime import datetime

from sqlalchemy import (
    Table,
    Column,
    Boolean,
    Integer,
    String,
    Text,
    Float,
)

# Database connection setup
URL_DATABASE = "postgresql://postgres:ShibaInu@127.0.0.1:5432/BoardGameVault"
engine = create_engine(URL_DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Database table definition
metadata = MetaData()
Boardgame = Table(
    "boardgames",
    metadata,
    Column("item_id", Integer, primary_key=True),
    Column("type", String),
    Column("name", String),
    Column("owned", Boolean, default=False),
    Column("times_played", Integer, default=0),
    Column("dates_played", Text),
    Column("comments", Text),
    Column("alternate_names", Text),
    Column("description", Text),
    Column("yearpublished", Integer),
    Column("minplayers", Integer),
    Column("maxplayers", Integer),
    Column("playingtime", Integer),
    Column("minplaytime", Integer),
    Column("maxplaytime", Integer),
    Column("age", Integer),
    Column("categories", Text),
    Column("mechanics", Text),
    Column("families", Text),
    Column("integrations", Text),
    Column("implementations", Text),
    Column("designers", Text),
    Column("artists", Text),
    Column("publishers", Text),
    Column("users_rated", Integer),
    Column("average_rating", Float),
    Column("bayes_average", Float),
    Column("bgg_rank", Integer),
    Column("num_weights", Integer),
    Column("average_weight", Float),
    Column("thumbnail", String),
    Column("image", String),
)


def create_database_tables() -> None:
    """
    Creates the database tables defined in the metadata object.
    """
    metadata.create_all(engine)


def insert_items_data(game_data: dict) -> None:
    """
    Inserts board games data into the database, checking for duplicates first.

    Args:
        game_data: A dictionary containing board games data.
    """
    with engine.begin() as conn:
        for new_item_id, data in game_data.items():
            is_boardgame = (
                data["type"] == "boardgame"
                or data["type"] == "boardgameexpansion"
                or data["type"] == "boardgameaccessory"
            )
            if is_boardgame:
                existing_game = conn.execute(
                    select(Boardgame).where(Boardgame.c.item_id == new_item_id)
                ).fetchone()
                if not existing_game:
                    conn.execute(insert(Boardgame).values(data))


def update_item_ownership(item_id: int) -> None:
    """
    Toggles the ownership status (owned/not owned) of a game in the database.

    Args:
        item_id: The ID of the game to update.
    """
    with engine.begin() as conn:
        current_status = conn.execute(
            select(Boardgame.c.owned).where(Boardgame.c.item_id == item_id)
        ).scalar()
        new_status = not current_status
        conn.execute(
            update(Boardgame)
            .where(Boardgame.c.item_id == item_id)
            .values(owned=new_status)
        )


def update_times_played(item_id: int, minus: bool) -> None:
    """
    Updates the number of times a game has been played, incrementing or decrementing as needed.

    Args:
        item_id: The ID of the game to update.
        minus: A boolean indicating whether to decrement the times played (True) or increment (False).
    """
    with engine.begin() as conn:
        current_status = conn.execute(
            select(Boardgame.c.times_played).where(Boardgame.c.item_id == item_id)
        ).scalar()
        current_dates_played = conn.execute(
            select(Boardgame.c.dates_played).where(Boardgame.c.item_id == item_id)
        ).scalar()

        dates_played_list = (
            current_dates_played.split(",") if current_dates_played else []
        )

        if minus and current_status > 0:
            new_status = current_status - 1
            if dates_played_list:
                dates_played_list.pop()
        elif not minus:
            new_status = current_status + 1
            dates_played_list.append(datetime.now().strftime("%Y-%m-%d"))

        new_dates_played = ",".join(dates_played_list)
        conn.execute(
            update(Boardgame)
            .where(Boardgame.c.item_id == item_id)
            .values(times_played=new_status, dates_played=new_dates_played)
        )


def update_comments(item_id: int, comment: str) -> None:
    """
    Updates the comments of a game in the database.

    Args:
        item_id: The ID of the game to update.
        comment: The new comment to set for the item.
    """
    with engine.begin() as conn:
        new_comments = comment
        conn.execute(
            update(Boardgame)
            .where(Boardgame.c.item_id == item_id)
            .values(comments=new_comments)
        )


def get_highest_id() -> int:
    """
    Retrieves the highest existing game ID from the boardgames table.

    Returns:
        The highest item ID, or 0 if the table is empty.
    """
    with engine.begin() as conn:
        highest_id = conn.execute(
            select(Boardgame).order_by(Boardgame.c.item_id.desc())
        ).first()
    if highest_id:
        return highest_id.item_id
    return 0
