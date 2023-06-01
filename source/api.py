"""
@created_by ayaan
@created_at 2023.05.08
"""
import random
import test
import traceback
from fastapi import FastAPI, UploadFile, status, Request
from fastapi.responses import JSONResponse
from custom_exception import APIException
from utils.azure_blob_storage_utils import AzureBlobStorageUtils
from utils.azure_openai_utils import AzureOpenAIUtils
from fastapi.middleware.cors import CORSMiddleware
from domains.bodies import ChatbotQuery, CreateContainerBody, DeleteBlobsBody
from azure.core.exceptions import AzureError
from database import MysqlEngine
from domains import crud
from sqlalchemy.orm import lazyload
from sqlalchemy import asc, desc

app = FastAPI()

origins = ["https://gentle-grass-0f33d3300.3.azurestaticapps.net"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=origins,
    allow_headers=origins,
)


@app.middleware("http")
async def errors_handling(request: Request, call_next):
    """Common Error Middleware"""
    try:
        return await call_next(request)
    except AzureError as azure_exc:
        return JSONResponse(status_code=500, content={"code": 500, "message": "Azure API에 문제가 발생하였습니다.", "error": str(azure_exc)})
    # except Exception as exc:
    #     return JSONResponse(status_code=500, content={"code": 500, "message": "에러가 발생하였습니다.", "error": str(exc)})


@app.exception_handler(APIException)
async def unicorn_exception_handler(request: Request, exc: APIException):
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


@app.get("/containers", status_code=status.HTTP_200_OK, tags=["Azure Blob Storage"])
async def containers_list():
    """Get container Names List

    Returns:
        list: container Names list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_containers()


@app.post("/containers", status_code=status.HTTP_201_CREATED, tags=["Azure Blob Storage"])
async def create_container(create_container_body: CreateContainerBody):
    """Create Container

    Args:
        name (CreateContainerBody): 이름

    Returns:
        _type_: _description_
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.create_container(create_container_body.name)


@app.delete("/containers/{container}", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def delete_container(container):
    """Create Container"""
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.delete_container(container)


@app.post("/containers/{container}/blobs", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def upload_blobs(container, file: UploadFile):
    """Upload Blob

    Args:
        file (UploadFile): Upload File

    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.upload_to_container(container, file, file.filename, file.content_type)


@app.delete("/containers/{container}/blobs", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def delete_blobs(container, delete_blobs_body: DeleteBlobsBody):
    """Delete Blobs"""
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.delete_blobs(container, delete_blobs_body.file_names)


@app.get("/containers/{container}/blobs", status_code=status.HTTP_200_OK, tags=["Azure Blob Storage"])
async def blobs_list(container):
    """Get Blobs List

    Returns:
        list: blob name list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_blobs(container)


@app.get("/indexes", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_index_list():
    """Get Cognitive Search Index List"""
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_index_list()


@app.get("/indexers", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_indexer_list():
    """Get Cognitive Search Indexer List"""
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_indexer_list()


@app.get("/indexers/{indexer}/status", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_indexer_status(indexer):
    """Get Cognitive Search Indexer Status

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.cognitive_search_get_indexer_status(indexer)


@app.post("/indexers/{indexer}/run", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Cognitive Search"])
async def run_indexer(indexer):
    """Cognitive Search Indexer Run

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    await azure_openai_utils.cognitive_search_run_indexer(indexer)


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
async def search():
    """test"""
    return test.test()
