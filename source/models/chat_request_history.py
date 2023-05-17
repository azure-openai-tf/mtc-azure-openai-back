from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.sql.expression import func
from database import MysqlEngine


class Statues:
    success: str = "success"
    fail: str = "fail"
    running: str = "running"


class ChatRequestHistory(MysqlEngine.mysql):
    __tablename__ = "chat_request_history"

    Statues = Statues

    id = Column(Integer, autoincrement=True, primary_key=True)
    selected_index = Column(String)
    created_at = Column(DATETIME(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DATETIME(timezone=True))
    response_at = Column(DATETIME(timezone=True))
    status = Column(String, nullable=False)
    created_user = Column(String, nullable=False)
    updated_user = Column(String)
    query = Column(String, nullable=False)
    answer = Column(String)
    reference_file = Column(String)
    running_time = Column(Integer, default=0)
