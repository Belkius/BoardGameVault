from pydantic import BaseModel


class BoardgamePydantic(BaseModel):
    """
    Pydantic model representing a board game in the database.

    This model maps to the columns in the 'boardgames' table and is used for data validation
    and serialization/deserialization purposes.
    """

    __tablename__ = "boardgames"

    item_id: int
    type: str
    name: str
    owned: bool
    times_played: int
    dates_played: str
    comments: str
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
