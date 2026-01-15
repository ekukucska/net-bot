from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class ActionLog(Base):
    """
    Log table for recording all network diagnostic actions.
    """
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    parameters = Column(Text, nullable=True)
    result_summary = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # success, error, partial
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ActionLog(id={self.id}, action={self.action}, status={self.status})>"


# Database setup
def get_database_url():
    """Get SQLite database URL"""
    # Store database in the project root
    db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "netbot.db")
    return f"sqlite:///{db_path}"


def init_db():
    """Initialize the database"""
    engine = create_engine(get_database_url(), echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Get a database session"""
    engine = init_db()
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionLocal()
