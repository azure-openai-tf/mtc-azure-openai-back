"""
@created_by ayaan
@created_at 2023.05.08
"""
import test
import traceback
from azure.core.exceptions import AzureError
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import MysqlEngine
from routers.blob_storage_router import blob_storage_router
from routers.cognitive_search_router import cognitive_search_router
from custom_exception import APIException
from utils.azure_openai_utils import AzureOpenAIUtils
from domains.bodies import ChatbotQuery

MysqlEngine.mysql.metadata.create_all(bind=MysqlEngine.engine)

app = FastAPI()
app.include_router(blob_storage_router)
app.include_router(cognitive_search_router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Common Error Middleware"""
    try:
        request.state.db = MysqlEngine.session()
        return await call_next(request)
    except AzureError as azure_exc:
        return JSONResponse(status_code=500, content={"code": 500, "message": "Azure API에 문제가 발생하였습니다.", "error": str(azure_exc)})
    finally:
        request.state.db.close()
    # except Exception as exc:
    #     return JSONResponse(status_code=500, content={"code": 500, "message": "에러가 발생하였습니다.", "error": str(exc)})


@app.exception_handler(APIException)
async def unicorn_exception_handler(exc: APIException):
    """Common Exception Handler

    Args:
        request (Request): Request
        exc (APIException): Api Exception

    Returns:
        json: {"message": "message", "code": 500, "error": "error Message"}
    """
    traceback.print_exc(exc)
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message, "code": exc.code, "error": exc.error},
    )


@app.get("/")
async def root():
    """Root"""
    return {"message": "Hello World"}


@app.get("/search", status_code=status.HTTP_200_OK, tags=["LangChain"])
async def search(query, index_name, vector_store="FAISS"):
    """Cognitive Search + ChatGPT Langchain 질의

    Args:
        indexer (str): Index Name
        query (str): 질문
        vector_store(str): 벡터 DB Store

    """
    azure_openai_utils = AzureOpenAIUtils()
    index_list = await azure_openai_utils.get_index_list()
    if len(list(filter(lambda x: x["index_name"] == index_name, index_list))) > 0:
        return await azure_openai_utils.execute_openai(query, index_name, vector_store)
    else:
        raise APIException(404, "Cognitive Search 인덱스를 찾을 수 없습니다.")


@app.post("/chatbot/query", status_code=status.HTTP_200_OK, tags=["ChatGPT"])
async def query_chatbot(chatbot_query: ChatbotQuery):
    """ChatGPT 3.5 질의

    Args:
        query (str): 질문
        messages (list, optional): Prompt

    Returns:ws
        dict: 답변 & Prompt
    """

    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.query_openai(chatbot_query.query, chatbot_query.messages)


@app.get("/chat-request-histories", status_code=status.HTTP_200_OK, tags=["Chat Request History"])
async def get_chat_request_histories():
    return crud.get_chat_request_histories()


@app.get("/test", status_code=status.HTTP_200_OK, tags=["Test"])
async def test():
    """test"""
    return test.test()
