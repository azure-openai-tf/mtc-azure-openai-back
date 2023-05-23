from fastapi import APIRouter, status
from utils.azure_openai_utils import AzureOpenAIUtils

cognitive_search_router = APIRouter()


@cognitive_search_router.get("/indexes", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_index_list():
    """Get Cognitive Search Index List"""
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_index_list()


@cognitive_search_router.get("/indexers", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_indexer_list():
    """Get Cognitive Search Indexer List"""
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_indexer_list()


@cognitive_search_router.get("/indexers/{indexer}/status", status_code=status.HTTP_200_OK, tags=["Azure Cognitive Search"])
async def get_indexer_status(indexer):
    """Get Cognitive Search Indexer Status

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.cognitive_search_get_indexer_status(indexer)


@cognitive_search_router.post("/indexers/{indexer}/run", status_code=status.HTTP_204_NO_CONTENT, tags=["Azure Cognitive Search"])
async def run_indexer(indexer):
    """Cognitive Search Indexer Run

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    await azure_openai_utils.cognitive_search_run_indexer(indexer)
