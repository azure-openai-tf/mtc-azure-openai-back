from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    status: str
    name: str
    email: str
    password: None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # chat_request_histories: list[ChatRequestHistory] = []
    # chat_request_likes = relationship("ChatRequestLike", back_populates="user")

    class Config:
        orm_mode = True


class ChatRequestHistoryBase(BaseModel):
    selected_index: str
    status: str
    query: str
    answer: str | None
    reference_file: str | None
    running_time: int


class ChatRequestHistory(ChatRequestHistoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    response_at: datetime
    user_id: int
    users: list[User] = []


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
