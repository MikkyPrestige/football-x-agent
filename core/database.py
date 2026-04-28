from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def init_db():
    """Create all tables. Safe to call multiple times."""
    import core.models  # ensure all models are registered
    Base.metadata.create_all(bind=engine)

def get_session():
    """Yield a database session to be used as a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
