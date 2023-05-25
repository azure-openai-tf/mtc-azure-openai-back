import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from dotenv import load_dotenv

load_dotenv()


class MysqlEngine:
    mysql_user = os.getenv("MYSQL_USER")
    mysql_password = os.getenv("MYSQL_PASSWORD")
    mysql_host = os.getenv("MYSQL_HOST")
    mysql_db_name = os.getenv("MYSQL_DB_NAME")
    database_url = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db_name}"

    engine = create_engine(database_url, echo=False)
    # session = sessionmaker(autocommit=True, autoflush=False, bind=engine)
    session = scoped_session(sessionmaker(bind=engine))

    mysql = declarative_base()
