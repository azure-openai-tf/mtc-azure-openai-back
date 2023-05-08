"""
@created_by ayaan
@created_at 2023.05.08
"""
import os
import urllib
import requests
from collections import OrderedDict
from IPython.display import display, HTML

# LangCahin & OpenAI 패키지
import langchain
import openai
from langchain.chat_models import AzureChatOpenAI
from langchain.vectorstores import FAISS
from langchain.vectorstores import Chroma
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

        # Azure OpenAI 연결 환경 변수 설정
        openai.api_type = "azure"  # 중요!
        openai.api_version = self.azure_openai_api_version  # 최신 preview 버전 2023-03-15-preview
        openai.api_base = self.azure_openai_endpoint
        openai.api_key = self.azure_openai_key

    async def execute_openai(self):
        """Excute OpenAI

        Returns:
            : _description_
        """

        # 질문 설정
        # QUESTION = 'How much is GPT-4 Uniform Bar Exam score? give me exact score number'

        # 질문 설정
        # QUESTION = ' Azure 관리자 자격증중에 어떤 자격증이 있는지 아주 간단히 설명해줘' --> 이 메시지를 넣으면 에러가 난다..
        question = " Azure 관리자가 되고 싶은데 어떻게 해야 하는지 자격증도 설명해주고 알려줘"

        # Azure Cognitive Search REST API 호출(get)

        index_name = "ai-azureblob-index"

        url = self.azure_search_endpoint + "/indexes/" + index_name + "/docs"
        url += "?api-version={}".format(self.azure_openai_api_version)
        url += "&search={}".format(QUESTION)  # 질문
        url += "&select=*"
        # url += '&$top=5'  # 문서 개수 제한
        url += "&queryLanguage=en-US"
        url += "&queryType=semantic"  # 의미 체계 검색
        url += "&semanticConfiguration=semantic-config"
        url += "&$count=true"
        url += "&speller=lexicon"  # 쿼리 맞춤법 검사
        url += "&answers=extractive|count-3"
        url += "&captions=extractive|highlight-false"

        params = {
            "api-version": self.azure_openai_api_version,
            "search": question,
            "queryLanguage": "en-US",
            "queryType": "semantic",
            "semanticConfiguration": "semantic-config",
            "select": "*",
            "$count": "true",
            "speller": "lexicon",
            "answers": "extractive|count-3",
            "captions": "extractive|highlight-false",
        }

        resp = requests.get(url, headers=headers)
        search_results = resp.json()  # 결과값

        print("API 호출 결과 :", resp.status_code)

        # print(search_results)
        # semantic-config 설정 꼭 필요
        print("검색 문서 수: {}, : 상위 문서 수: {}".format(search_results["@odata.count"], len(search_results["value"])))

        display(HTML("<h4>상위 연관 문서</h4>"))

        file_content = OrderedDict()
        for result in search_results["value"]:
            # print('result : ' , result)
            # print(result['@search.rerankerScore'])
            # print('file_content : ', file_content)
            print("path : ", result["metadata_storage_path"])
            if result["@search.rerankerScore"] > 0.04:  # Semantic Search 최대 점수 4점, 상위 40%
                # print('##########################################################################################################')
                display(HTML("<h1>" + str(result["metadata_storage_name"]) + ", score: " + str(result["@search.rerankerScore"]) + "</h1>"))
                display(HTML(result["@search.captions"][0]["text"]))
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
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", chunk_size=1, openai_api_key=AZURE_OPENAI_KEY)  # Azure OpenAI embedding 사용시 주의
        # Vector Store 생성
        # vevtor_store = FAISS.from_documents(docs, embeddings)
        # Chroma vector db에 넣음
        persist_directory = "db"
        vevtor_store = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_directory)
        # vevtor_store = Chroma.from_documents(docs, embeddings)

        # LangChain🦜 & Azure GPT🤖 연결
        # llm = AzureChatOpenAI(deployment_name='gpt-35-turbo',  openai_api_key=AZURE_OPENAI_KEY, openai_api_base=AZURE_OPENAI_ENDPOINT, openai_api_version=AZURE_OPENAI_API_VERSION,
        llm = AzureChatOpenAI(
            deployment_name="gpt-35-turbo",
            openai_api_key=AZURE_OPENAI_KEY,
            openai_api_base=AZURE_OPENAI_ENDPOINT,
            openai_api_version=AZURE_OPENAI_API_VERSION,
            temperature=0.0,
            max_tokens=1000,
        )

        # https://python.langchain.com/en/latest/modules/chains/index_examples/qa_with_sources.html
        qa = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            # chain_type='stuff',
            chain_type="map_reduce",
            retriever=vevtor_store.as_retriever(),
            return_source_documents=True,
        )

        print(qa)

        result = qa({"question": QUESTION})
        # 답변 글자수 카운트
        # char_counts=0
        # ls_str = list(map(str,result))
        # for ls_str1 in ls_str:
        #   char_counts = char_counts + len(ls_str1)

        # print(char_counts)

        print("질문 :", QUESTION)
        print("답변 :", result["answer"])
        print("📄 참고 자료 :", result["sources"].replace(",", "\n"))
