from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Text, Float

URL_DATABASE =

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Boardgame(Base):
    __tablename__ = "boardgames"

    objectid = Column(Integer, primary_key=True)
    type = Column(String)
    name = Column(String)
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
    families = Column(Text)
    integrations = Column(Text)
    implementations = Column(Text)
    designers = Column(Text)
    artists = Column(Text)
    publishers = Column(Text)
    usersrated = Column(Integer)
    average_rating = Column(Float)
    bayes_average = Column(Float)
    bgg_rank = Column(Integer)
    numweights = Column(Integer)
    average_weights = Column(Float)
    thumbnail = Column(String)
    image = Column(String)


def create_database_tables():
    Base = declarative_base()

    class Boardgame(Base):
        __tablename__ = "boardgames"

        objectid = Column(Integer, primary_key=True)
        type = Column(String)
        name = Column(String)
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
        families = Column(Text)
        integrations = Column(Text)
        implementations = Column(Text)
        designers = Column(Text)
        artists = Column(Text)
        publishers = Column(Text)
        usersrated = Column(Integer)
        average_rating = Column(Float)
        bayes_average = Column(Float)
        bgg_rank = Column(Integer)
        numweights = Column(Integer)
        average_weights = Column(Float)
        thumbnail = Column(String)
        image = Column(String)

    Base.metadata.create_all(engine)


def insert_game_data(session, game_data):
    for objectid, data in game_data.items():
        new_game = Boardgame(**data)
        session.add(new_game)
    session.commit()
