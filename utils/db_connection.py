from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from utils.logger import logger
from config.config import DB_USER, DB_PASS, DB_NAME, DB_HOST


# Define the database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Configure session maker (optionally using scoped_session if multithreading is required)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def get_db():
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # Rollback the session on error
        logger.error(f"Database session rollback due to error: {e}")
        raise e
    finally:
        db.close()
