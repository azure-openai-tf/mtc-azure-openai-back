"""
@created_by ayaan
@created_at 2023.05.08
"""
import os
import requests
from collections import OrderedDict
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.aio import SearchIndexerClient

# LangCahin & OpenAI 패키지
import openai
from langchain.chat_models import AzureChatOpenAI
# from langchain.vectorstores import Chroma
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings

from dotenv import load_dotenv

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
        return await search_indexer_client.get_indexer_status(indexer_name)

    async def execute_openai(self, question, index_name, vector_store_name):
        """Excute OpenAI"""
        # 질문 설정
        # QUESTION = ' Azure 관리자 자격증중에 어떤 자격증이 있는지 아주 간단히 설명해줘' --> 이 메시지를 넣으면 에러가 난다..
        question = " Azure 관리자가 되고 싶은데 어떻게 해야 하는지 자격증도 설명해주고 알려줘"

        # Azure Cognitive Search REST API 호출(get)
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
            "$top=5": "5",
            "answers": "extractive|count-3",
            "captions": "extractive|highlight-false",
        }

        resp = requests.get(url, params=params, headers=self.headers)
        search_results = resp.json()  # 결과값

        print("API 호출 결과 :", resp.status_code)

        # print(search_results)
        # semantic-config 설정 꼭 필요
        # print(search_results)
        print(f"검색 문서 수: {search_results['@odata.count']}, : 상위 문서 수: {len(search_results['value'])}")

        # display(HTML("<h4>상위 연관 문서</h4>"))

        file_content = OrderedDict()
        for result in search_results["value"]:
            # print('result : ' , result)
            # print(result['@search.rerankerScore'])
            # print('file_content : ', file_content)
            print("path : ", result["metadata_storage_path"])
            if result["@search.rerankerScore"] > 0.04:  # Semantic Search 최대 점수 4점, 상위 40%
                # print('##########################################################################################################')
                # display(HTML("<h1>" + str(result["metadata_storage_name"]) + ", score: " + str(result["@search.rerankerScore"]) + "</h1>"))
                # display(HTML(result["@search.captions"][0]["text"]))
                file_content[result["metadata_storage_path"]] = {
                    "chunks": result["pages"][:1],
                    "caption": result["@search.captions"][0]["text"],
                    "score": result["@search.rerankerScore"],
                    "file_name": result["metadata_storage_name"],
                }
                # print('file_content : ', file_content)

        # AzureOpenAI Service 연결
        # 문서 분할
        docs = []
        for key, value in file_content.items():
            # print('key : ' , key , '\t value : ' , value)
            # print(value['chunks'])
            for page in value["chunks"]:
                docs.append(Document(page_content=page, metadata={"source": value["file_name"]}))
        print("Number of chunks:", len(docs))
        # print('#####################################################')
        # print('docs : ' , docs)

        # Embedding 모델 생성
        # 아래소스에서 chunk_size=1 이 아닌 다른 값을 넣으면 다음 소스에서 에러가 난다.
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002", chunk_size=1, openai_api_key=self.azure_openai_key
        )  # Azure OpenAI embedding 사용시 주의
        
        # Vector Store 생성
        persist_directory = "db"
        vector_store = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_directory)
        vector_store = Chroma.from_documents(docs, embeddings)
        if vector_store_name == 'FAISS':
            vector_store = FAISS.from_documents(docs, embeddings)

        # LangChain🦜 & Azure GPT🤖 연결
        # llm = AzureChatOpenAI(deployment_name='gpt-35-turbo',  openai_api_key=AZURE_OPENAI_KEY, openai_api_base=AZURE_OPENAI_ENDPOINT, openai_api_version=AZURE_OPENAI_API_VERSION,
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

        print(qa)

        result = qa({"question": question})
        # 답변 글자수 카운트
        # char_counts=0
        # ls_str = list(map(str,result))
        # for ls_str1 in ls_str:
        #   char_counts = char_counts + len(ls_str1)

        # print(char_counts)

        print("질문 :", question)
        print("답변 :", result["answer"])
        print("📄 참고 자료 :", result["sources"].replace(",", "\n"))

        return result["answer"]
