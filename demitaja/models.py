"""SQLAlchemy model and table definitions."""

from sqlalchemy import Table, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from demitaja.database import Base


postings_cities_assoc = Table(
    'postings_cities',
    Base.metadata,
    Column('posting_id', Integer, ForeignKey('postings.id')),
    Column('city_id', Integer, ForeignKey('cities.id'))
)


postings_must_assoc = Table(
    'postings_techs_must',
    Base.metadata,
    Column('posting_id', Integer, ForeignKey('postings.id')),
    Column('must_id', Integer, ForeignKey('technologies.id'))
)


postings_nice_assoc = Table(
    'postings_techs_nice',
    Base.metadata,
    Column('posting_id', Integer, ForeignKey('postings.id')),
    Column('nice_id', Integer, ForeignKey('technologies.id'))
)


class Posting(Base):
    """This class defines attributes of job posting and metadata of the
    table to which this class is mapped.
    Attributes:
        id (int): id of the posting
        web_id(str): posting's id on the source website
        title (str): job title
        posted (int): posted timestamp
        scraped (int): scraped timestamp
        text (str): posting's full text
    """
    __tablename__ = 'postings'
    id = Column(Integer, primary_key=True)
    web_id = Column(String(80), nullable=False)
    title = Column(String(80), nullable=False)
    posted = Column(Integer, nullable=False)
    scraped = Column(Integer, nullable=False)
    text = Column(String(5000), nullable=False)
    cities = relationship("City",
                          secondary=postings_cities_assoc,
                          back_populates="postings")
    techs_must = relationship("Technology",
                              secondary=postings_must_assoc,
                              back_populates="postings_must")
    techs_nice = relationship("Technology",
                              secondary=postings_nice_assoc,
                              back_populates="postings_nice")
    salaries = relationship("Salary",
                            cascade="all, delete-orphan",
                            back_populates="posting")


class City(Base):
    """This class defines attributes of city and metadata of the
    table to which this class is mapped.
    Attributes:
        id (int): id of the city
        name (str): name of the city
        name_ascii (str): lowercase ascii version of the city's name
    """
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    name_ascii = Column(String(80), nullable=False)
    postings = relationship("Posting",
                            secondary=postings_cities_assoc,
                            back_populates="cities")


class Technology(Base):
    """This class defines attributes of technology and metadata of the
    table to which this class is mapped.
    Attributes:
        id (int): id of the technology
        name (str): name of the technology
        name_ascii (str): lowercase ascii version of the technology's name
    """
    __tablename__ = 'technologies'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    name_ascii = Column(String(80), nullable=False)
    postings_must = relationship("Posting",
                                 secondary=postings_must_assoc,
                                 back_populates="techs_must")
    postings_nice = relationship("Posting",
                                 secondary=postings_nice_assoc,
                                 back_populates="techs_nice")


class Salary(Base):
    """This class defines attributes of salary and metadata of the
   table to which this class is mapped.
   Attributes:
       id (int): id of the salary
       posting_id (int): id of the parent posting
       employment_type_ascii (str): employment type in lowercase ascii
       salary_from (int): min salary
       salary_to (int): max salary
       salary_currency (str): currency of the salary
       salary_period (str): salary period
    """
    __tablename__ = 'salaries'
    id = Column(Integer, primary_key=True)
    posting_id = Column(Integer, ForeignKey('postings.id'))
    employment_type_ascii = Column(String(80))
    salary_from = Column(Integer)
    salary_to = Column(Integer)
    salary_currency = Column(String(80))
    salary_period = Column(String(80))
    posting = relationship("Posting",
                           back_populates="salaries")
