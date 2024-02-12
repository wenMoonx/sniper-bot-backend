from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
from sqlalchemy.ext.hybrid import hybrid_property
import uuid
import datetime

class User(Base):
  __tablename__ = 'users'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  username = Column(String)
  public_address = Column(String)
  nonce = Column(Integer)
  wallet_count = Column(Integer, default=0)
  created_at = Column(DateTime, default=datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)