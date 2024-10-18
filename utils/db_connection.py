from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from utils.logger import logger
from config.config import DB_USER, DB_PASS, DB_NAME, DB_HOST
from models.base import Base

# These imports are necessary for SQLAlchemy to detect and create all tables
# even if they're not directly used in this file
from models.user_model import User  # noqa: F401
from models.session_model import Session  # noqa: F401
from models.summary_model import Summary  # noqa: F401

__all__ = ['get_db', 'init_db', 'create_tables']

# Define the database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:25060/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Configure session maker (optionally using scoped_session if multithreading is required)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()  # Rollback the session on error
        logger.error(f"Database session rollback due to error: {e}")
        raise e
    finally:
        db.close()

def create_tables():
    """Create all tables defined in the models if they don't exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            table.create(engine)
            logger.info(f"Created table: {table.name}")
        else:
            logger.info(f"Table already exists: {table.name}")

def init_db():
    """Initialize the database by creating all tables."""
    try:
        create_tables()
        logger.info("Database initialized successfully.")
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()