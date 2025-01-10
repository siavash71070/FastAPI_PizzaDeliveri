from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "postgresql://postgres:ASDqwe123!@localhost:5432/pizza_delivery"
engine = create_engine(DATABASE_URL,
                       echo=True
                       )
Base = declarative_base()
Session = sessionmaker()