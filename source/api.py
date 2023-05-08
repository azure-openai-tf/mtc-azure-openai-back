"""
@created_by ayaan
@created_at 2023.05.08
"""
from datetime import datetime
from typing import Union, Optional
from fastapi import FastAPI, UploadFile, Response, status, Form
from utils.azure_blob_storage_utils import AzureBlobStorageUtils
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}", status_code=status.HTTP_200_OK)
async def read_item(item_id):
    return Response(content={"item_id": item_id})


@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


@app.get("/blobs/", status_code=status.HTTP_200_OK)
async def blobs_list():
    """Get Blobs List

    Returns:
        list: blob name list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_blobs()


@app.get("/blobs/downloadfile", status_code=status.HTTP_200_OK)
async def get_blob():
    """Download File

    Args:
        file (UploadFile): Upload File



    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_blobs()


@app.post("/blobs/uploadfile", status_code=status.HTTP_204_NO_CONTENT)
async def blobs_upload_file(file: UploadFile):
    """Blob Upload File

    Args:
        file (UploadFile): Upload File

    """
    azure_blob_storage_utils = AzureBlobStorageUtils()
    await azure_blob_storage_utils.upload_to_azure(file, file.filename, file.content_type)
