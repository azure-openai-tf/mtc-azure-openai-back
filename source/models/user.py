from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DATETIME
from sqlalchemy.sql.expression import func
from database import MysqlEngine
from sqlalchemy.orm import relationship 


class Statues:
    active: str = "active"
    inactive: str = "inactive"


class User(MysqlEngine.mysql):
    __tablename__ = "user"

    Statues = Statues

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DATETIME(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DATETIME(timezone=True))
    status = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String)
    chat_request_histories = relationship("ChatRequestHistory", back_populates="user")
