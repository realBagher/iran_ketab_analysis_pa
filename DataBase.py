
from sqlalchemy import create_engine, MetaData, create_engine, ForeignKey
from sqlalchemy import Table, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Sequence
from urllib.parse import quote_plus
from sqlalchemy.orm import sessionmaker


#%%
meta = MetaData()
USERNAME = 'root'
PASSWORD = '1393ram1393#$'
SERVER = 'localhost'
engine = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}:3306/', echo=True)
conn = engine.connect()
database_name = 'IranKetab_scraper'
create_database_query = f"CREATE DATABASE {database_name}"
conn.execute(create_database_query)


#%%
engine = create_engine(f'mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER}:3306/IranKetab_scraper', echo=True)
conn = engine.connect()


#%%
Base = declarative_base()

# Define SQLAlchemy table classes


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    ISBN = Column(String(13), unique=True)
    persian_name = Column(String(255))
    english_name = Column(String(255))
    rate = Column(Float)


class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, unique=True)
    name = Column(String(32))
    book_id = Column(Integer, ForeignKey("book.id"))
    role = Column(String(8))


class Price(Base):
    __tablename__ = 'price'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    price = Column(Float)
    net_price = Column(Float)
    discount_percent = Column(Float)
    current_price = Column(Float)  # for change price in interval time


class Publisher(Base):
    __tablename__ = 'publisher'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    name = Column(String(32))


class BookDetails(Base):
    __tablename__ = 'book_details'

    book_id = Column(Integer, ForeignKey("book.id"), primary_key=True)
    size = Column(String(32))
    num_page = Column(Integer)
    cover_type = Column(String(32))


class ReleaseDate(Base):
    __tablename__ = 'release_date'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("book.id"))
    shpy = Column(DateTime)  # solar hijri publication year
    gpy = Column(DateTime)  # gregorian publication year
    print_series = Column(Integer)  # print series of the book


class BookDescription(Base):
    __tablename__ = 'book_description'

    book_id = Column(Integer, ForeignKey("book.id"), primary_key=True)
    content = Column(Text)


class PersonDescription(Base):
    __tablename__ = 'person_description'

    id = Column(Integer, primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey("person.person_id"))
    description = Column(Text)


class BookCategory(Base):
    __tablename__ = 'book_category'

    book_id = Column(Integer, ForeignKey("book.id"), primary_key=True)
    categories = Column(String(255))

#%%


Base.metadata.create_all(engine)

#%%
Session = sessionmaker(bind=engine)
session = Session()


