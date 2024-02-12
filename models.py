from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey
from database import Base

class Games(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)