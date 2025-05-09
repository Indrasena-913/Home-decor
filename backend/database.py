
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
load_dotenv()

SQL_DATABASE_URL=os.getenv("SQL_DATABASE_URL")

engine=create_engine(SQL_DATABASE_URL)
SessionLocal=sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base=declarative_base()


