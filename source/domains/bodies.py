"""
@created_by ayaan
@created_at 2023.05.12
"""
from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

DB_URL = 'mysql.connector.connect(user="openaiAdmin", password="{password}", host="mtc-openai-db-mysql.mysql.database.azure.com", port=3306, database="{database}", ssl_ca="{ca-cert filename}", ssl_disabled=False)'


class CreateContainerBody(BaseModel):
    """CreateContainerBody"""

    name: str


class LoginBody(BaseModel):
    """LoginBody"""

    id: str
    password: str


class DeleteBlobsBody(BaseModel):
    """DeleteBlobsBody"""

    file_names: list[str | None] = []


class ChatbotQuery(BaseModel):
    """ChatbotQuery"""

    query: str
    messages: list = []
