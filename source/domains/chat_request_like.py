# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DATETIME
# from sqlalchemy.sql.expression import func
# from database import MysqlEngine
# from sqlalchemy.orm import relationship


# class Statues:
#     success: str = "success"
#     fail: str = "fail"
#     running: str = "running"


# class ChatRequestLike(MysqlEngine.mysql):
#     __tablename__ = "chat_request_like"

#     Statues = Statues

#     id = Column(Integer, autoincrement=True, primary_key=True)
#     selected_index = Column(String)
#     created_at = Column(DATETIME(timezone=True), nullable=False, default=func.now())
#     updated_at = Column(DATETIME(timezone=True))
#     deleted_at = Column(DATETIME(timezone=True))
#     status = Column(String, nullable=False)
#     is_like = Column(Integer)
#     # user_id = Column(Integer, ForeignKey("user.id"))
#     # user = relationship(User, back_populates="chat_request_like")
#     # chat_request_history_id = Column(Integer, ForeignKey("chat_request_history.id"))
#     # chat_request_histories = relationship(ChatRequestHistory, back_populates="chat_request_like")
