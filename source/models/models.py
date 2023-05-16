"""
@created_by ayaan
@created_at 2023.05.12
"""
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

DB_URL = 'mysql.connector.connect(user="openaiAdmin", password="{password}", host="mtc-openai-db-mysql.mysql.database.azure.com", port=3306, database="{database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)'

class ChatbotQuery(BaseModel):
    """ChatbotQuery"""
    
    def __init__(self):
        self.engine = create_engine(DB_URL, pool_recycle = 500)

    def sessionmaker(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def connection(self):
        conn = self.engine.connect()
        return conn   
    
    query: str
    messages: list = []
