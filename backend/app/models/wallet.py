from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
import uuid
import datetime

class Wallet(Base):
  __tablename__ = 'wallets'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  wallet_address = Column(String)
  private_key = Column(String)
  user = Column(String)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)