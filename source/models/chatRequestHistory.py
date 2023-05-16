
from sqlalchemy import Column, TEXT, DATETIME, INT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

Base = declarative_base()

class ChatRequestHistory(Base):

    __tablename__ = 'chat_request_history'

    id = Column("id", INT, nullable=False, autoincrement=True, primary_key=True)
    selectedIndex = Column("selected_index", TEXT)
    requestAt = Column("request_at", DATETIME(timezone=True))
    requestMessage = Column("request_message", TEXT, default='')
    responseAt = Column("response_at", DATETIME(timezone=True))
    responseMessage = Column("response_message", TEXT, default='')
    responseCode = Column("response_code", TEXT, default='')
    referenceFile = Column("reference_file", TEXT, default='')
    createAt = Column("create_at", DATETIME(timezone=True), default=func.now())
    createUser = Column("create_user", TEXT, default='')
    updateAt = Column("update_at", DATETIME(timezone=True))
    updateUser = Column("update_user", TEXT)
    