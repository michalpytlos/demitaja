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
        employment_type (str): employment type
        salary_from (int): min salary
        salary_to (int): max salary
        salary_currency (str): currency of the salary
        salary_period (str): salary period
    """
    __tablename__ = 'postings'
    id = Column(Integer, primary_key=True)
    web_id = Column(String(80), nullable=False)
    title = Column(String(80), nullable=False)
    posted = Column(Integer, nullable=False)
    scraped = Column(Integer, nullable=False)
    text = Column(String(5000), nullable=False)
    employment_type = Column(String(80))
    salary_from = Column(Integer)
    salary_to = Column(Integer)
    salary_currency = Column(String(80))
    salary_period = Column(String(80))
    cities = relationship("City",
                          secondary=postings_cities_assoc,
                          back_populates="postings")
    techs_must = relationship("Technology",
                              secondary=postings_must_assoc,
                              back_populates="postings_must")
    techs_nice = relationship("Technology",
                              secondary=postings_nice_assoc,
                              back_populates="postings_nice")


class City(Base):
    """This class defines attributes of city and metadata of the
    table to which this class is mapped.
    Attributes:
        id (int): id of the city
        name (str): name of the city
    """
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    postings = relationship("Posting",
                            secondary=postings_cities_assoc,
                            back_populates="cities")


class Technology(Base):
    """This class defines attributes of technology and metadata of the
    table to which this class is mapped.
    Attributes:
        id (int): id of the technology
        name (str): name of the technology
    """
    __tablename__ = 'technologies'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    postings_must = relationship("Posting",
                                 secondary=postings_must_assoc,
                                 back_populates="techs_must")
    postings_nice = relationship("Posting",
                                 secondary=postings_nice_assoc,
                                 back_populates="techs_nice")
