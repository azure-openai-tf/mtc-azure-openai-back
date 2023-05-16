
from sqlalchemy import Column, TEXT, DATETIME, INT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func

Base = declarative_base()

class ChatRequestHistory(Base):

    __tablename__ = 'chat_request_history'

    id = Column("id", INT, nullable=False, autoincrement=True, primary_key=True)
    selected_index = Column("selected_index", TEXT)
    request_at = Column("request_at", DATETIME(timezone=True))
    request_message = Column("request_message", TEXT, default='')
    response_at = Column("response_at", DATETIME(timezone=True))
    response_message = Column("response_message", TEXT, default='')
    response_code = Column("response_code", TEXT, default='')
    reference_file = Column("reference_file", TEXT, default='')
    create_at = Column("create_at", DATETIME(timezone=True), default=func.now())
    create_user = Column("create_user", TEXT, default='')
    update_at = Column("update_at", DATETIME(timezone=True))
    update_user = Column("update_user", TEXT)
    
def openAiRequestToModelRequest(params):
    print(params)
    result = {

    }
    return ""

def openAiResponseToModelResponse(params):
    print(params)
    result = {

    }
    return ""