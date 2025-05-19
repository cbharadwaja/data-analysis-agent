from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.sql import func
from services.database import Base

class RawData(Base):
    __tablename__ = 'raw_data'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())