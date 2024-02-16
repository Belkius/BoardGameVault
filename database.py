from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Text, Float

URL_DATABASE = 'postgresql://postgres:ShibaInu@localhost:5432/BoardGameVault'

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Boardgame(Base):
    __tablename__ = "boardgames"

    item_id = Column(Integer, primary_key=True)
    type = Column(String)
    name = Column(String)
    owned = Column(Boolean, default=False)
    alternate_names = Column(Text)
    description = Column(Text)
    yearpublished = Column(Integer)
    minplayers = Column(Integer)
    maxplayers = Column(Integer)
    playingtime = Column(Integer)
    minplaytime = Column(Integer)
    maxplaytime = Column(Integer)
    age = Column(Integer)
    categories = Column(Text)
    mechanics = Column(Text)
    families = Column(Text)
    integrations = Column(Text)
    implementations = Column(Text)
    designers = Column(Text)
    artists = Column(Text)
    publishers = Column(Text)
    users_rated = Column(Integer)
    average_rating = Column(Float)
    bayes_average = Column(Float)
    bgg_rank = Column(Integer)
    num_weights = Column(Integer)
    average_weight = Column(Float)
    thumbnail = Column(String)
    image = Column(String)


def create_database_tables():
    Base.metadata.create_all(engine)


def insert_items_data(session, game_data):
    for id, data in game_data.items():
        existing_game = session.query(Boardgame).filter_by(item_id=id).first()
        if not existing_game:
            new_game = Boardgame(**data)
            session.add(new_game)
    session.commit()

def get_highest_id(session):
    highest_id = session.query(Boardgame).order_by(Boardgame.item_id.desc()).first()
    return highest_id.item_id
