from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# classes
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(140), nullable=False)
    password = Column(String(140), nullable=False)
    children = relationship("Book")


class Book(Base):
    __tablename__='book'

    id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    author = Column(String(250), nullable=False)
    genre = Column(String(250))
    read = Column(Boolean)
    user_id = Column(Integer, ForeignKey('user.id'))


engine = create_engine('sqlite:///books-collection.db')
Base.metadata.create_all(engine)
