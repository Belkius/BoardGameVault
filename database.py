from sqlalchemy import create_engine, MetaData, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, select

from sqlalchemy import (
    Table,
    Column,
    Boolean,
    Integer,
    String,
    Text,
    Float,
)

URL_DATABASE = "postgresql://postgres:ShibaInu@localhost:5432/BoardGameVault"

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    metadata.create_all(engine)


def insert_items_data(game_data: dict) -> None:
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
    with engine.begin() as conn:
        current_status = conn.execute(
            select(Boardgame.c.times_played).where(Boardgame.c.item_id == item_id)
        ).scalar()
        if minus:
            new_status = current_status - 1
        else:
            new_status = current_status + 1
        conn.execute(
            update(Boardgame)
            .where(Boardgame.c.item_id == item_id)
            .values(times_played=new_status)
        )


def get_highest_id() -> int:
    with engine.begin() as conn:
        highest_id = conn.execute(
            select(Boardgame).order_by(Boardgame.c.item_id.desc())
        ).first()
        return highest_id.item_id
