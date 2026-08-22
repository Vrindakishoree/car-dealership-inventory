from sqlmodel import SQLModel, create_engine, Session

# SQLite database file will be created automatically
DATABASE_URL = "sqlite:///./dealership.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    """Creates all tables based on our SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Provides a database session for each request."""
    with Session(engine) as session:
        yield session