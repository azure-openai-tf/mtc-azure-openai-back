from fastapi import APIRouter, status, UploadFile
from domains.bodies import CreateContainerBody, DeleteBlobsBody
from utils.azure_blob_storage_utils import AzureBlobStorageUtils

blob_storage_router = APIRouter()


@blob_storage_router.get("/containers", status_code=status.HTTP_200_OK, tags=["Azure Blob Storage"])
async def containers_list():
    """Get container Names List

    Returns:
        list: container Names list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_containers()


@blob_storage_router.post("/containers", status_code=status.HTTP_201_CREATED, tags=["Azure Blob Storage"])
async def create_container(create_container_body: CreateContainerBody):
    """Create Container

    Args:
        name (CreateContainerBody): 이름

    Returns:
        _type_: _description_
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.create_container(create_container_body.name)


@blob_storage_router.delete("/containers/{container}", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def delete_container(container):
    """Create Container"""
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.delete_container(container)


@blob_storage_router.post("/containers/{container}/blobs", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def upload_blobs(container, file: UploadFile):
    """Upload Blob

    Args:
        file (UploadFile): Upload File

    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.upload_to_container(container, file, file.filename, file.content_type)


@blob_storage_router.delete("/containers/{container}/blobs", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Blob Storage"])
async def delete_blobs(container, delete_blobs_body: DeleteBlobsBody):
    """Delete Blobs"""
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.delete_blobs(container, delete_blobs_body.file_names)


@blob_storage_router.get("/containers/{container}/blobs", status_code=status.HTTP_200_OK, tags=["Azure Blob Storage"])
async def blobs_list(container):
    """Get Blobs List

    Returns:
        list: blob name list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_blobs(container)
