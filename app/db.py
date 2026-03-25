from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# À adapter avec tes identifiants Postgres
DATABASE_URL = "postgresql+psycopg2://forest_user:1234@localhost:5432/forest_db"
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

