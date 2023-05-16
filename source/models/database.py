from sqlalchemy import *
from sqlalchemy.orm import sessionmaker


DB_URL = 'mysql://openaiAdmin:@.mysql.database.azure.com:3306/openai'
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