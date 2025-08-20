from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

DB_FILE = Path(__file__).parent / 'forms.db'
engine = create_engine(f'sqlite:///{DB_FILE}', connect_args={'check_same_thread': False})

db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

def init_db():
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
