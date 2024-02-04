from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from app.core.conf import settings

username = settings.DB_USER
password = settings.DB_PASSWORD
host = settings.DB_HOST
port = settings.DB_PORT
dbname = settings.DB_NAME

engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/{dbname}")

if not database_exists(engine.url):
  create_database(engine.url)

Session = sessionmaker(engine)
session = Session(future=True)