"""Database settings."""

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from demitaja import app


engine = create_engine(app.config['DB_URL'], echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Initialize database."""
    import demitaja.models
    Base.metadata.create_all(bind=engine)
    print('Done!')
