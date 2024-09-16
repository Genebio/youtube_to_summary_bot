import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base import Base

# Fetch database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")

# Validate environment variables
if not all([DB_USER, DB_PASS, DB_NAME, DB_HOST]):
    raise ValueError("Missing one or more required environment variables: DB_USER, DB_PASS, DB_NAME, DB_HOST")

# Define the database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)  # Set echo=True for debugging SQL queries in logs

# Configure session maker (optionally using scoped_session if multithreading is required)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # Rollback the session on error
        raise e
    finally:
        db.close()

# Create all tables in the database (only run this once during setup)
Base.metadata.create_all(bind=engine)