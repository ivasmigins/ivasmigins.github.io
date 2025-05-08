from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timezone

base = declarative_base()

class TemperatureData(base):
    __tablename__ = 'temperature_data'
    id = Column(Integer, primary_key=True)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

engine = create_engine('sqlite:///temperature_data.db')
base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
