from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CountdownEvent(Base):
    __tablename__ = "countdown_events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    target_date = Column(DateTime)
    chat_id = Column(Integer)  # Telegram chat ID where the event was created
    created_by = Column(Integer)  # Telegram user ID who created the event
    daily_reminder = Column(Boolean, default=False)
    created_at = Column(DateTime)
    timezone = Column(String, default="Europe/Berlin")  # Default timezone for the event

    def __repr__(self):
        return f"<CountdownEvent(name='{self.name}', target_date='{self.target_date}')>"

# Create all tables
Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 