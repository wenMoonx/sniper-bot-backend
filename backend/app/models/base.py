from sqlalchemy.orm import declarative_base
from app.models.common import Common

Base = declarative_base(cls=Common)