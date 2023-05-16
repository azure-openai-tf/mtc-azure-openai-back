from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import os

azure_mysql_username = os.environ.get("AZURE_MYSQL_USER")
azure_mysql_password = os.environ.get("AZURE_MYSQL_PASSWORD")
azure_mysql_db = os.environ.get("AZURE_MYSQL_NAME")
azure_mysql_host = os.environ.get("AZURE_MYSQL_HOST")

DB_URL = 'mysql://{azure_mysql_username}:{azure_mysql_password}@{azure_mysql_host}/{azure_mysql_db}'
class engineconn:

    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn