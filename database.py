from sqlalchemy import create_engine, MetaData
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

metadata = MetaData()

Boardgame = Table(
    "boardgames",
    metadata,
    Column("item_id", Integer, primary_key=True),
    Column("type", String),
    Column("name", String),
    Column("owned", Boolean, default=False),
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


def create_database_tables():
    metadata.create_all(engine)

def insert_items_data(game_data):
    with engine.begin() as conn:
        for id, data in game_data.items():
            existing_game = conn.execute(select(Boardgame).where(Boardgame.c.item_id == id)).fetchone()
            if not existing_game:
                conn.execute(insert(Boardgame).values(data))


def get_highest_id():
    with engine.begin() as conn:
        highest_id = conn.execute(select(Boardgame).order_by(Boardgame.c.item_id.desc())).first()
        return highest_id.item_id
