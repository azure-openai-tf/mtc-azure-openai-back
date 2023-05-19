from database import MysqlEngine
from domains import models, schemas


def get_chat_request_histories():
    return MysqlEngine.session.query(models.ChatRequestHistory).all()
