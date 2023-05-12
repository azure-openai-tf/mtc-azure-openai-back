"""
@created_by ayaan
@created_at 2023.05.08
"""
import os
from azure.storage.blob.aio import BlobServiceClient
from dotenv import load_dotenv
from fastapi import UploadFile
from custom_exception import APIException

load_dotenv()


# blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net", credential=DefaultAzureCredential())


class AzureBlobStorageUtils:
    """Azure Blob Stroage Utilities"""

    azure_storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    azure_storage_key = os.getenv("AZURE_STORAGE_KEY")
    azure_container_name = os.getenv("AZURE_CONTAINER_NAME")

    def __init__(self):
        connection_str = f"DefaultEndpointsProtocol=https;AccountName={self.azure_storage_account};AccountKey={self.azure_storage_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_str)
        self.container_client = self.blob_service_client.get_container_client(self.azure_container_name)

    async def list_blobs(self):
        """List Blob

        Returns:
            list : blob Names
        """
        blobs_list = []
        async for blob in self.container_client.list_blobs():
            blobs_list.append(blob.name)

        return blobs_list

    async def upload_to_azure(self, file: UploadFile, file_name: str, content_type: str):
        """Upload To Azure

        Args:
            file (UploadFile): 파일객체
            file_name (str): 파일명
            content_type (str): content-type
        """

        async with self.blob_service_client:
            try:
                blob_client = self.container_client.get_blob_client(file_name)
                file_bytes = await file.read()
                await blob_client.upload_blob(file_bytes, content_type=content_type)
            except Exception as ex:
                raise APIException(500, "파일 업로드에 실패하였습니다.", str(ex))
