"""
@created_by ayaan
@created_at 2023.05.08
"""
import os
from azure.storage.blob.aio import BlobServiceClient, ContainerClient
from dotenv import load_dotenv
from fastapi import UploadFile
from custom_exception import APIException
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError, HttpResponseError

load_dotenv()


# blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net", credential=DefaultAzureCredential())


class AzureBlobStorageUtils:
    """Azure Blob Stroage Utilities"""

    azure_storage_account = os.getenv("AZURE_STORAGE_ACCOUNT")
    azure_storage_key = os.getenv("AZURE_STORAGE_KEY")

    def __init__(self):
        self.connection_str = f"DefaultEndpointsProtocol=https;AccountName={self.azure_storage_account};AccountKey={self.azure_storage_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_str)
        # self.container_client = self.blob_service_client.get_container_client(container_name)

    async def list_containers(self):
        """List Container

        Returns:
            list : Container Names
        """
        container_list = []
        try:
            async for container in self.blob_service_client.list_containers():
                container_list.append(container.name)
            return container_list
        finally:
            await self.blob_service_client.close()

    async def list_blobs(self, container_name):
        """List Blob

        Returns:
            list : blob Names
        """
        container_client = None
        blobs_list = []
        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            async for blob in container_client.list_blobs():
                blobs_list.append(blob.name)

            return blobs_list
        except ResourceNotFoundError as exp:
            raise APIException(404, "컨테이너를 찾을 수 없습니다.", str(exp))
        finally:
            await self.close_client(container_client)

    async def create_container(self, container_name: str):
        """Create Contrainer"""
        container_client = None

        try:
            container_client = await self.blob_service_client.create_container(name=container_name)
            result = await container_client.get_container_properties()

            return result
        except ResourceExistsError as ex:
            raise APIException(400, "중복된 컨테이너가 존재합니다.", str(ex))
        except HttpResponseError as exp:
            raise APIException(400, "컨테이너명이 형식에 맞지 않습니다.", str(exp))
        finally:
            await self.close_client(container_client)

    async def delete_container(self, container_name: str):
        """Delete Contrainer"""
        container_client = self.blob_service_client.get_container_client(container_name)

        try:
            await container_client.delete_container()
        except ResourceNotFoundError as ex:
            raise APIException(404, "컨테이너를 찾을 수 없습니다.", str(ex))
        except HttpResponseError as exc:
            raise APIException(404, "컨테이너명이 형식에 맞지 않습니다.", str(exc))
        finally:
            await self.close_client(container_client)

    async def upload_to_container(self, container_name: str, file: UploadFile, file_name: str, content_type: str):
        """Upload To Azure

        Args:
            file (UploadFile): 파일객체
            file_name (str): 파일명
            content_type (str): content-type
        """
        container_client = self.blob_service_client.get_container_client(container_name)

        async with self.blob_service_client:
            try:
                blob_client = container_client.get_blob_client(file_name)
                file_bytes = await file.read()
                await blob_client.upload_blob(file_bytes, content_type=content_type)

            except ResourceExistsError as exc:
                raise APIException(400, "중복된 파일이 존재합니다.", str(exc))
            except Exception as ex:
                raise APIException(500, "파일 업로드에 실패하였습니다.", str(ex))
            finally:
                await self.close_client(container_client)

    async def delete_blobs(self, container_name: str, file_names: list[str]):
        """Delete Blobs

        Args:
            file (UploadFile): 파일객체
            file_name (str): 파일명
            content_type (str): content-type
        """

        blobs_list = await self.list_blobs(container_name)

        for file_name in file_names:
            if not file_name in blobs_list:
                raise APIException(404, "삭제할 파일을 찾을 수 없습니다.")

        # container_client = self.blob_service_client.get_container_client(container_name)
        container_client = ContainerClient.from_connection_string(self.connection_str, container_name)

        try:
            for file_name in file_names:
                await container_client.delete_blob(blob=file_name)
                # await container_client.delete_blobs(file_name)

        finally:
            await self.close_client(container_client)

    async def close_client(self, container_client: None | ContainerClient):
        """close_container_client"""
        if container_client:
            print("Container Client Close")
            await container_client.close()
        if self.blob_service_client:
            print("Blob Service Client Close")
            await self.blob_service_client.close()
