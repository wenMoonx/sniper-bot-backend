from sqlalchemy import Column, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import uuid
import datetime

class PresaleSnipe(Base):
  __tablename__ = 'presale_snipe'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  wallet_address = Column(String)
  pair = Column(String)
  currency = Column(String)
  token = Column(String)
  presale_contract = Column(String)
  status = Column(String)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)