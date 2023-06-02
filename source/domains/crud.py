from domains import models
from sqlalchemy import desc


def get_offset(page, size) -> int:
    """get offset"""
    return (page - 1) * size


def get_chat_request_histories(session, page, size):
    """get_chat_request_histories"""
    return session.query(models.ChatRequestHistory).order_by(desc(models.ChatRequestHistory.id)).offset(get_offset(page, size)).limit(size).all()
