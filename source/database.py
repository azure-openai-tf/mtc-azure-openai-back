"""
@created_by ayaan
@created_at 2023.05.23
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv()


class MysqlEngine:
    """MYSQL Engine"""

    __mysql_user = os.getenv("MYSQL_USER")
    __mysql_password = os.getenv("MYSQL_PASSWORD")
    __mysql_host = os.getenv("MYSQL_HOST")
    __mysql_db_name = os.getenv("MYSQL_DB_NAME")
    __database_url = f"mysql+pymysql://{__mysql_user}:{__mysql_password}@{__mysql_host}/{__mysql_db_name}"

    engine = create_engine(__database_url, echo=True)
    # session = sessionmaker(autocommit=True, autoflush=False, bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mysql = declarative_base()
