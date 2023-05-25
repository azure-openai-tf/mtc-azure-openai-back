"""
@created_by ayaan
@created_at 2023.05.08
"""
import os
import requests
import time
from custom_exception import APIException
from utils.common_utils import CommonUtils
from collections import OrderedDict
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.aio import SearchIndexerClient
from azure.search.documents.indexes.aio import SearchIndexClient

# LangCahin & OpenAI 패키지
import openai
from langchain.chat_models import AzureChatOpenAI

# from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv

# Log DB Insert
from database import MysqlEngine
from domains.models import ChatRequestHistory

load_dotenv()


class AzureOpenAIUtils:
    """Azure OpenAI Utilities"""

    azure_search_key = os.environ.get("SEARCH_KEY")
    azure_search_endpoint = os.environ.get("SEARCH_ENDPOINT")
    azure_search_api_version = "2021-04-30-preview"
    azure_openai_key = os.environ.get("OPEN_AI_KEY")
    azure_openai_endpoint = os.environ.get("OPEN_AI_ENDPOINT")
    azure_openai_api_version = "2023-03-15-preview"

    def __init__(self):
        self.headers = {"Content-Type": "application/json", "api-key": self.azure_search_key}
        self.params = {"api-version": self.azure_search_api_version}  # 최신 Preview 버전 2021-04-30-preview

        self.cognitive_search_credential = AzureKeyCredential(self.azure_search_key)

        # Azure OpenAI 연결 환경 변수 설정
        openai.api_type = "azure"  # 중요!
        openai.api_version = self.azure_openai_api_version  # 최신 preview 버전 2023-03-15-preview
        openai.api_base = self.azure_openai_endpoint
        openai.api_key = self.azure_openai_key

    async def get_index(self, index_name):
        """cognitive Search Get Index"""
        search_index_client = SearchIndexClient(self.azure_search_endpoint, self.cognitive_search_credential)
        index = await search_index_client.get_index(index_name)
        await search_index_client.close()
        return index

    async def get_indexer(self, indexer_name):
        """cognitive Search Get Indexer"""
        search_indexer_client = SearchIndexerClient(self.azure_search_endpoint, self.cognitive_search_credential)
        indexer = await search_indexer_client.get_index(indexer_name)
        await search_indexer_client.close()
        return indexer

    async def get_index_list(self):
        """cognitive Search Get Index List"""
        search_index_client = SearchIndexClient(self.azure_search_endpoint, self.cognitive_search_credential)
        index_list = []
        async for index in search_index_client.list_indexes():
            index_list.append({"index_name": index.name})

        await search_index_client.close()

        return index_list

    async def get_indexer_list(self):
        """cognitive Search Get Indexer List"""
        search_indexer_client = SearchIndexerClient(self.azure_search_endpoint, self.cognitive_search_credential)
        indexer_list = []
        for indexer in await search_indexer_client.get_indexers():
            indexer_list.append({"indexer_name": indexer.name, "target_index_name": indexer.target_index_name})

        await search_indexer_client.close()

        return indexer_list

    async def cognitive_search_run_indexer(self, index_name):
        """cognitive_search_run_indexer"""
        search_indexer_client = SearchIndexerClient(self.azure_search_endpoint, self.cognitive_search_credential)
        # indexer = await search_indexer_client.get_indexer(indexer_name)
        await search_indexer_client.run_indexer(index_name)

        await search_indexer_client.close()
        print("index 업데이트 완료")

    async def cognitive_search_get_indexer_status(self, indexer_name):
        """cognitive_search_get_indexer_status"""
        search_indexer_client = SearchIndexerClient(self.azure_search_endpoint, self.cognitive_search_credential)
        # indexer = await search_indexer_client.get_indexer(indexer_name)
        result = await search_indexer_client.get_indexer_status(indexer_name)

        await search_indexer_client.close()
        return result

    async def query_openai(self, query, messages):
        """Query Open AI

        Args:
            query (str): 질의
            messages (list): Messages

        Returns:
            dict: messages & answer
        """
        if len(messages) == 0:
            messages = [
                {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                {"role": "user", "content": query},
            ]
        else:
            messages.append({"role": "user", "content": query})

        response = openai.ChatCompletion.create(engine="chat", messages=messages)
        messages.append(response["choices"][0]["message"])

        result = {"messages": messages, "answer": response["choices"][0]["message"]["content"]}

        return result

    async def execute_openai(self, question, index_name, vector_store_name):
        """Excute OpenAI"""
        return_dict = {"question": question, "answer": '자료를 찾지 못하였습니다.', "reference_file": ""}
        # 로그 저장
        start = time.time()
        chat_request_history = ChatRequestHistory(selected_index=index_name, query="test", user_id=22, status=ChatRequestHistory.Statues.running)
        MysqlEngine.session.add(chat_request_history)
        MysqlEngine.session.commit()

        # Call Cognitive API
        url = self.azure_search_endpoint + "/indexes/" + index_name + "/docs"
        params = {
            "api-version": self.azure_search_api_version,
            "search": question,
            "queryLanguage": "en-US",
            "queryType": "semantic",
            "semanticConfiguration": "semantic-config",
            "select": "*",
            "$count": "true",
            "speller": "lexicon",
            "$top": "5",
            "answers": "extractive|count-3",
            "captions": "extractive|highlight-false",
        }

        resp = requests.get(url, params=params, headers=self.headers)
        search_results = resp.json()  # 결과값

        if resp.status_code != 200:
            chat_request_history.answer = return_dict['answer']
            chat_request_history.status = ChatRequestHistory.Statues.fail
            chat_request_history.response_at = CommonUtils.get_kst_now()
            chat_request_history.running_time = CommonUtils.get_running_time(start, time.time())
            MysqlEngine.session.commit()
            raise APIException(resp.status_code, "Cognitive Search API 실패", error=resp.json())

        if search_results["@odata.count"] == 0:
            chat_request_history.answer = return_dict['answer']
            chat_request_history.status = ChatRequestHistory.Statues.success
            chat_request_history.response_at = CommonUtils.get_kst_now()
            chat_request_history.running_time = CommonUtils.get_running_time(start, time.time())
            MysqlEngine.session.commit()
            return return_dict
        else:
            file_content = OrderedDict()
            for result in search_results["value"]:
                if result["@search.rerankerScore"] > 0.04:  # Semantic Search 최대 점수 4점, 상위 40%
                    file_content[result["metadata_storage_path"]] = {
                        "chunks": result["pages"][:1],
                        "caption": result["@search.captions"][0]["text"],
                        "score": result["@search.rerankerScore"],
                        "file_name": result["metadata_storage_name"],
                    }

            # AzureOpenAI Service 연결
            docs = []
            for key, value in file_content.items():
                for page in value["chunks"]:
                    docs.append(Document(page_content=page, metadata={"source": value["file_name"]}))

            if len(docs) == 0:
                chat_request_history.answer = return_dict['answer']
                chat_request_history.status = ChatRequestHistory.Statues.success
                chat_request_history.response_at = CommonUtils.get_kst_now()
                chat_request_history.running_time = CommonUtils.get_running_time(start, time.time())
                MysqlEngine.session.commit()
                return return_dict

            # Embedding 모델 생성
            # 아래소스에서 chunk_size=1 이 아닌 다른 값을 넣으면 다음 소스에서 에러가 난다.
            embeddings = OpenAIEmbeddings(
                model="text-similarity-curie-001", chunk_size=1, openai_api_key=self.azure_openai_key
            )  # Azure OpenAI embedding 사용시 주의

            # Vector Store 생성
            vector_store = FAISS.from_documents(docs, embeddings)
            # if vector_store_name == 'Chroma':
            # persist_directory = "db"
            # 	vector_store = Chroma.from_documents(docs, embeddings)
            # 	vector_store = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_directory)

            # LangChain🦜 & Azure GPT🤖 연결
            llm = AzureChatOpenAI(
                deployment_name="chat",
                openai_api_key=self.azure_openai_key,
                openai_api_base=self.azure_openai_endpoint,
                openai_api_version=self.azure_openai_api_version,
                temperature=0.0,
                max_tokens=1000,
            )

            # https://python.langchain.com/en/latest/modules/chains/index_examples/qa_with_sources.html
            qa = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,
                # chain_type='stuff',
                chain_type="map_reduce",
                retriever=vector_store.as_retriever(),
                return_source_documents=True,
            )

            result = qa({"question": question})

            print("질문 :", question)
            print("답변 :", result["answer"])
            print("📄 참고 자료 :", result["sources"].replace(",", "\n"))
            return_dict['answer'] = result['answer']
            return_dict['reference_file'] = result["sources"].replace(",", "\n")

            chat_request_history.answer = result["answer"]
            chat_request_history.status = ChatRequestHistory.Statues.success
            chat_request_history.response_at = CommonUtils.get_kst_now()
            chat_request_history.running_time = CommonUtils.get_running_time(start, time.time())
            chat_request_history.reference_file = result["sources"].replace(",", "\n")
            MysqlEngine.session.commit()

            return return_dict
