"""
@created_by ayaan
@created_at 2023.05.08
"""
from fastapi import FastAPI, UploadFile, status, Request
from fastapi.responses import JSONResponse
from custom_exception import APIException
from utils.azure_blob_storage_utils import AzureBlobStorageUtils
from utils.azure_openai_utils import AzureOpenAIUtils
from fastapi.middleware.cors import CORSMiddleware
from domains.bodies import ChatbotQuery, CreateContainerBody, DeleteBlobsBody, LoginBody
from azure.core.exceptions import AzureError
from database import MysqlEngine
from domains import crud

app = FastAPI()

origins = ["https://gentle-grass-0f33d3300.3.azurestaticapps.net", "http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def errors_handling(request: Request, call_next):
    """Common Error Middleware"""
    try:
        request.state.session = MysqlEngine.session()
        return await call_next(request)
    # except AzureError as azure_exc:
    #     request.state.session.rollback()
    #     return JSONResponse(status_code=500, content={"code": 500, "message": "Azure API에 문제가 발생하였습니다.", "error": str(azure_exc)})
    # except Exception as exc:
    #     request.state.session.rollback()
    #     return JSONResponse(status_code=500, content={"code": 500, "message": "에러가 발생하였습니다.", "error": str(exc)})
    finally:
        request.state.session.close()


@app.exception_handler(APIException)
async def unicorn_exception_handler(request: Request, exc: APIException):
    """Common Exception Handler

    Args:
        request (Request): Request
        exc (APIException): Api Exception

    Returns:
        json: {"message": "message", "code": 500, "error": "error Message"}
    """
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message, "code": exc.code, "error": exc.error},
    )


@app.get("/")
async def root():
    """Root"""
    return {"message": "Hello World"}


@app.post("/login", tags=["Login"])
async def login(login_body: LoginBody):
    """Login"""
    if login_body.id == "admin" and login_body.password == "mtcopenaitf1234!":
        return "success"
    else:
        raise APIException(401, "ID 또는 Password가 일치하지 않습니다.", "Unauthorized")


@app.get("/containers", status_code=status.HTTP_200_OK, tags=["Azure Blob Storage"])
async def containers_list():
    """컨테이너 이름 목록 가져오기

    Returns:
        list: container Names list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_containers()


@app.post("/containers", status_code=status.HTTP_201_CREATED, tags=["Azure Blob Storage"])
async def create_container(create_container_body: CreateContainerBody):
    """컨테이너 생성

    Args:
        name (CreateContainerBody): 이름

    Returns:
        dict: Blob 정보
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.create_container(create_container_body.name)


@app.delete("/containers/{container}", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def delete_container(container):
    """컨테이너 삭제

    Args:
        container (str): 컨테이너 이름
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.delete_container(container)


@app.post("/containers/{container}/blobs", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def upload_blobs(container, file: UploadFile):
    """컨테이너에 Blob파일 업로드

    Args:
        container (str): 컨테이너 이름
        file (UploadFile): 파일
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.upload_to_container(container, file, file.filename, file.content_type)


@app.delete("/containers/{container}/blobs", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def delete_blobs(container, delete_blobs_body: DeleteBlobsBody):
    """컨테이너에 Blob파일 다중 삭제

    Args:
        container (str): 컨테이너 이름
        file_names (list): ['test.txt', 'test2'.txt] 파일명들

    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.delete_blobs(container, delete_blobs_body.file_names)


@app.get("/containers/{container}/blobs", status_code=status.HTTP_200_OK, tags=["Azure Blob Storage"])
async def blobs_list(container):
    """컨테이너에 파일 목록 조회

    Args:
        container (str): 컨테이너 이름

    Returns:
        list: 컨테이너 파일 목록
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_blobs(container)


@app.get("/indexes", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_index_list():
    """인덱스 목록 조회

    Returns:
        list: 인덱스 목록 [{"index_name": index.name}]
    """
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_index_list()


@app.get("/indexers", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_indexer_list():
    """Cognitive Search Indexer 목록 조회

    Returns:
        list: 인덱서 목록 [{"indexer_name": indexer.name, "target_index_name": indexer.target_index_name}]
    """
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_indexer_list()


@app.get("/indexers/{indexer}/status", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_indexer_status(indexer):
    """Cognitive Search Indexer 상태 조회

    Args:
        indexer (str): Indexer Name
    """
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.cognitive_search_get_indexer_status(indexer)


@app.post("/indexers/{indexer}/run", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Cognitive Search"])
async def run_indexer(indexer):
    """Cognitive Search Indexer 실행

    Args:
        indexer (str): Indexer Name
    """
    azure_openai_utils = AzureOpenAIUtils()
    await azure_openai_utils.cognitive_search_run_indexer(indexer)


@app.get("/search", status_code=status.HTTP_200_OK, tags=["LangChain"])
async def search(request: Request, query, index_name, vector_store="FAISS"):
    """Cognitive Search + ChatGPT Langchain 질의

    Args:
        indexer (str): Index Name
        query (str): 질문
        vector_store(str): 벡터 DB Store 이름 (FAISS/chroma)

    """
    azure_openai_utils = AzureOpenAIUtils()
    index_list = await azure_openai_utils.get_index_list()
    if len(list(filter(lambda x: x["index_name"] == index_name, index_list))) > 0:
        return await azure_openai_utils.execute_openai(request.state.session, query, index_name, vector_store)
    else:
        raise APIException(404, "Cognitive Search 인덱스를 찾을 수 없습니다.")


@app.get("/searchv2", status_code=status.HTTP_200_OK, tags=["LangChain"])
async def searchv2(request: Request, query, index_name, vector_store="FAISS"):
    """Cognitive Search + ChatGPT Langchain 질의

    Args:
        indexer (str): Index Name
        query (str): 질문
        vector_store(str): 벡터 DB Store 이름 (FAISS/chroma)

    """
    azure_openai_utils = AzureOpenAIUtils()
    index_list = await azure_openai_utils.get_index_list()
    if len(list(filter(lambda x: x["index_name"] == index_name, index_list))) > 0:
        return await azure_openai_utils.execute_openai_v2(request.state.session, query, index_name, vector_store)
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
async def get_chat_request_histories(request: Request, page: int = 1, size: int = 10):
    """채팅 목록 조회

    Args:
        page (int, optional): 페이지 번호. Defaults to 1.
        size (int, optional): 페이지 크기. Defaults to 10.

    Returns:
        dict: {"page": 1, "size":10, items: []}
    """
    return {"page": page, "size": size, "items": crud.get_chat_request_histories(request.state.session, page, size)}
