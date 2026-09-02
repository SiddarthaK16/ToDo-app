from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")





engine= create_engine(SQLALCHEMY_DATABASE_URI,connect_args={"check_same_thread":False})
#check_same_thread is cuz of FastAPI supports multiple threads.. so

# sessionmaker → creates database session factory
# autocommit=False → manually commit changes using db.commit()
# autoflush=False → don't automatically flush pending changes
# bind=engine → use our database engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()