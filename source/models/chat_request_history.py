from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.sql.expression import func
from database import MysqlEngine
# from models.chat_request_like import ChatRequestLike
from models.user import User
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property


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
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User, back_populates="chat_request_history")
    query = Column(String, nullable=False)
    answer = Column(String)
    reference_file = Column(String)
    running_time = Column(Integer, default=0)
    # chat_request_likes = relationship(ChatRequestLike, backref="chat_request_history")
    
    @hybrid_property
    def chat_request_like_count(self):
        return len(self.chat_request_likes)
