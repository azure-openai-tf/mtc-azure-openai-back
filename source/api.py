"""
@created_by ayaan
@created_at 2023.05.08
"""
import random
from fastapi import FastAPI, UploadFile, status, Request
from fastapi.responses import JSONResponse
from custom_exception import APIException
from utils.azure_blob_storage_utils import AzureBlobStorageUtils
from utils.azure_openai_utils import AzureOpenAIUtils
from fastapi.middleware.cors import CORSMiddleware
from models.models import ChatbotQuery

app = FastAPI()

origins = ["*"]

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
    except Exception as exc:
        return JSONResponse(status_code=500, content={"code": 500, "error": str(exc)})


@app.get("/")
async def root():
    """Root"""
    return {"message": "Hello World"}


@app.exception_handler(APIException)
async def unicorn_exception_handler(request: Request, exc: APIException):
    """Common Exception Handler

    Args:
        request (Request): Request
        exc (APIException): Api Exception

    Returns:
        json: {"message": "message", "code": 500, "error": "error Message"}
    """
    print(request)
    return JSONResponse(
        status_code=exc.code,
        content={"message": exc.message, "code": exc.code, "error": exc.error},
    )


@app.get("/blobs", status_code=status.HTTP_200_OK)
async def blobs_list():
    """Get Blobs List

    Returns:
        list: blob name list
    """
    azure_blob_storage_utils = AzureBlobStorageUtils()

    return await azure_blob_storage_utils.list_blobs()


@app.get("/blobs/downloadfile", status_code=status.HTTP_200_OK)
async def get_blob():
    """Get Blob"""
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

    print("업로드 완료")
    azure_openai_utils = AzureOpenAIUtils()
    await azure_openai_utils.cognitive_search_run_indexer("ai-azureblob-indexer")


@app.get("/indexes", status_code=status.HTTP_200_OK)
async def get_index_list():
    """Get Cognitive Search Index List"""
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.get_index_list()


@app.get("/indexers/{indexer}/status", status_code=status.HTTP_200_OK)
async def get_indexer_status(indexer):
    """Get Cognitive Search Indexer Status

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.cognitive_search_get_indexer_status(indexer)


@app.post("/indexers/{indexer}/run", status_code=status.HTTP_204_NO_CONTENT)
async def run_indexer(indexer):
    """Cognitive Search Indexer Run

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    await azure_openai_utils.cognitive_search_run_indexer(indexer)


@app.get("/search", status_code=status.HTTP_200_OK)
async def search(query, index_name, vector_store="FAISS"):
    """Cognitive Search + ChatGPT Langchain 질의

    Args:
        indexer (str): Indexer Name

    """
    azure_openai_utils = AzureOpenAIUtils()
    index_list = await azure_openai_utils.get_index_list()

    if index_name in index_list:
        return await azure_openai_utils.execute_openai(query, index_name, vector_store)
    else:
        raise APIException(404, "Cognitive Search 인덱스를 찾을 수 없습니다.")


@app.post("/chatbot/query", status_code=status.HTTP_200_OK)
async def query_chatbot(chatbot_query: ChatbotQuery):
    """ChatGPT 3.5 질의

    Args:
        query (str): 질문
        messages (list, optional): Prompt

    Returns:
        dict: 답변 & Prompt
    """

    azure_openai_utils = AzureOpenAIUtils()
    return await azure_openai_utils.query_openai(chatbot_query.query, chatbot_query.messages)


@app.get("/chatbot/search", status_code=status.HTTP_200_OK)
async def chatbot(query):
    """100대 명언 샘플로 나중에 지울 예정"""
    lst = [
        "삶이 있는 한 희망은 있다 -키케로",
        "산다는것 그것은 치열한 전투이다. -로망로랑",
        "하루에 3시간을 걸으면 7년 후에 지구를 한바퀴 돌 수 있다. -사무엘존슨",
        "언제나 현재에 집중할수 있다면 행복할것이다. -파울로 코엘료",
        "진정으로 웃으려면 고통을 참아야하며 , 나아가 고통을 즐길 줄 알아야 해 -찰리 채플린",
        "직업에서 행복을 찾아라. 아니면 행복이 무엇인지 절대 모를 것이다 -엘버트 허버드",
        "신은 용기있는자를 결코 버리지 않는다 -켄러",
        "행복의 문이 하나 닫히면 다른 문이 열린다 그러나 우리는 종종 닫힌 문을 멍하니 바라보다가",
        "우리를 향해 열린 문을 보지 못하게 된다 – 헬렌켈러",
        "피할수 없으면 즐겨라 – 로버트 엘리엇",
        "단순하게 살아라. 현대인은 쓸데없는 절차와 일 때문에 얼마나 복잡한 삶을 살아가는가?-이드리스 샤흐",
        "먼저 자신을 비웃어라. 다른 사람이 당신을 비웃기 전에 – 엘사 맥스웰",
        "먼저핀꽃은 먼저진다 남보다 먼저 공을 세우려고 조급히 서둘것이 아니다 – 채근담",
        "행복한 삶을 살기위해 필요한 것은 거의 없다. -마르쿠스 아우렐리우스 안토니우스",
        "절대 어제를 후회하지 마라 . 인생은 오늘의 나 안에 있고 내일은 스스로 만드는 것이다 L.론허바드",
        "어리석은 자는 멀리서 행복을 찾고, 현명한 자는 자신의 발치에서 행복을 키워간다 -제임스 오펜하임",
        "너무 소심하고 까다롭게 자신의 행동을 고민하지 말라 . 모든 인생은 실험이다 . 더많이 실험할수록 더나아진다 – 랄프 왈도 에머슨",
        "한번의 실패와 영원한 실패를 혼동하지 마라 -F.스콧 핏제랄드",
        "내일은 내일의 태양이 뜬다",
        "피할수 없으면 즐겨라 -로버트 엘리엇",
        "절대 어제를 후회하지 마라. 인생은 오늘의 내 안에 있고 내일은 스스로 만드는것이다. -L론허바드",
        "계단을 밟아야 계단 위에 올라설수 있다, -터키속담",
        "오랫동안 꿈을 그리는 사람은 마침내 그 꿈을 닮아 간다, -앙드레 말로",
        "좋은 성과를 얻으려면 한 걸음 한 걸음이 힘차고 충실하지 않으면 안 된다, -단테",
        "행복은 습관이다,그것을 몸에 지니라 -허버드",
        "성공의 비결은 단 한 가지, 잘할 수 있는 일에 광적으로 집중하는 것이다.- 톰 모나건",
        "자신감 있는 표정을 지으면 자신감이 생긴다 -찰스다윈",
        "평생 살 것처럼 꿈을 꾸어라.그리고 내일 죽을 것처럼 오늘을 살아라. – 제임스 딘",
        "네 믿음은 네 생각이 된다 . 네 생각은 네 말이 된다. 네말은 네 행동이 된다 네행동은 네 습관이된다 . 네 습관은 네 가치가 된다 . 네 가치는 네 운명이 된다 – 간디",
        "일하는 시간과 노는 시간을 뚜렷이 구분하라 . 시간의 중요성을 이해하고 매순간을 즐겁게 보내고 유용하게 활용하라. 그러면 젋은 날은 유쾌함으로 가득찰것이고 늙어서도 후회할 일이 적어질것이며 비록 가난할 때라도 인생을 아름답게 살아갈수있다 – 루이사 메이올콧",
        "절대 포기하지 말라. 당신이 되고 싶은 무언가가 있다면, 그에 대해 자부심을 가져라. 당신 자신에게 기회를 주어라. 스스로가 형편없다고 생각하지 말라. 그래봐야 아무 것도 얻을 것이 없다. 목표를 높이 세워라.인생은 그렇게 살아야 한다. – 마이크 맥라렌",
        "1퍼센트의 가능성, 그것이 나의 길이다. -나폴레옹",
        "그대 자신의 영혼을 탐구하라.다른 누구에게도 의지하지 말고 오직 그대 혼자의 힘으로 하라. 그대의 여정에 다른 이들이 끼어들지 못하게 하라. 이 길은 그대만의 길이요, 그대 혼자 가야할 길임을 명심하라. 비록 다른 이들과 함께 걸을 수는 있으나 다른 그 어느 누구도 그대가 선택한 길을 대신 가줄 수 없음을 알라. -인디언 속담",
        "고통이 남기고 간 뒤를 보라! 고난이 지나면 반드시 기쁨이 스며든다. -괴테",
        "삶은 소유물이 아니라 순간 순간의 있음이다 영원한 것이 어디 있는가 모두가 한때일뿐 그러나 그 한때를 최선을 다해 최대한으로 살수 있어야 한다 삶은 놀라운 신비요 아름다움이다. 법정스님 -버리고 떠나기",
        "꿈을 계속 간직하고 있으면 반드시 실현할 때가 온다. -괴테",
        "화려한 일을 추구하지 말라. 중요한 것은 스스로의 재능이며, 자신의 행동에 쏟아 붓는 사랑의 정도이다. -머더 테레사",
        "마음만을 가지고 있어서는 안된다. 반드시 실천하여야 한다. -이소룡",
        "흔히 사람들은 기회를 기다리고 있지만 기회는 기다리는 사람에게 잡히지 않는 법이다. 우리는 기회를 기다리는 사람이 되기 전에 기회를 얻을 수 있는 실력을 갖춰야 한다. 일에 더 열중하는 사람이 되어야한다. -안창호",
        "나이가 60이다 70이다 하는 것으로 그 사람이 늙었다 젊었다 할 수 없다. 늙고 젊은 것은 그 사람의 신념이 늙었느냐 젊었느냐 하는데 있다. -맥아더",
        "만약 우리가 할 수 있는 일을 모두 한다면 우리들은 우리자신에 깜짝 놀랄 것이다. -에디슨",
        "나는 누구인가 스스로 물으라 자신의 속얼굴이 드러나 보일 때까지 묻고 묻고 물어야 한다건성으로 묻지말고 목소리 속의 목소리로 귀 속의 귀에 대고 간절하게 물어야 한다해답은 그 물음 속에 있다. 법정스님- 산에는 꽃이 피네",
        "행복은 결코 많고 큰데만 있는 것이 아니다 작은 것을 가지고도 고마워 하고 만족할 줄 안다면 그는 행복한 사람이다. 여백과 공간의 아름다움은 단순함과 간소함에 있다. 법정스님 – 홀로사는 즐거움 에서",
        "물러나서 조용하게 구하면 배울 수 있는 스승은 많다. 사람은 가는 곳마다 보는 것마다 모두 스승으로서 배울 것이 많은 법이다. -맹자",
        "눈물과 더불어 빵을 먹어 보지 않은 자는 인생의 참다운 맛을 모른다. -괴테",
        "진짜 문제는 사람들의 마음이다. 그것은 절대로 물리학이나 윤리학의 문제가 아니다. -아인슈타인",
        "해야 할 것을 하라. 모든 것은 타인의 행복을 위해서, 동시에 특히 나의 행복을 위해서이다. -톨스토이",
        "사람이 여행을 하는 것은 도착하기 위해서가 아니라 여행하기 위해서이다. -괴테",
        "화가 날 때는 100까지 세라. 최악일 때는 욕설을 퍼부어라. -마크 트웨인",
        "재산을 잃은 사람은 많이 잃은 것이고, 친구를 잃은 사람은 더많이 잃은 것이며, 용기를 잃은 사람은 모든것을 잃은 것이다. -세르반테스",
        "돈이란 바닷물과도 같다. 그것은 마시면 마실수록 목이 말라진다. -쇼펜하우어",
        "이룰수 없는 꿈을 꾸고 이길수 없는 적과 싸우며, 이룰수 없는 사랑을 하고 견딜 수 없는 고통을 견디고, 잡을수 없는 저 하늘의 별도 잡자. -세르반테스",
        "고개 숙이지 마십시오. 세상을 똑바로 정면으로 바라보십시오. -헬렌 켈러",
        "고난의 시기에 동요하지 않는 것, 이것은 진정 칭찬받을 만한 뛰어난 인물의 증거다. -베토벤",
        "사막이 아름다운 것은 어딘가에 샘이 숨겨져 있기 때문이다 – 생떽쥐베리",
        "행복의 한 쪽 문이 닫히면 다른 쪽 문이 열린다. 그러나 흔히 우리는 닫혀진 문을 오랫동안 보기 때문에 우리를 위해 열려 있는 문을 보지 못한다. -헬렌 켈러",
        "만족할 줄 아는 사람은진정한 부자이고, 탐욕스러운 사람은진실로 가난한 사람이다. -솔론",
        "성공해서 만족하는 것은 아니다. 만족하고 있었기 때문에 성공한 것이다.-알랭",
        "곧 위에 비교하면 족하지 못하나,아래에 비교하면 남음이 있다. -명심보감",
        "그대의 하루 하루를 그대의 마지막 날이라고 생각하라 – 호라티우스",
        "자신을 내보여라. 그러면 재능이 드러날 것이다. – 발타사르 그라시안",
        "자신의 본성이 어떤것이든 그에 충실하라 . 자신이 가진 재능의 끈을 놓아 버리지 마라. 본성이 이끄는 대로 따르면 성공할것이다 -시드니 스미스",
        "당신이 할수 있다고 믿든 할수 없다고 믿든 믿는 대로 될것이다.- 헨리 포드",
        "단순하게 살라. 쓸데없는 절차와 일 때문에 얼마나 복잡한 삶을 살아가는가? -이드리스 샤흐",
        "당신이 인생의 주인공이기 때문이다 . 그사실을 잊지마라 . 지금까지 당신이 만들어온 의식적 그리고 무의식적 선택으로 인해 지금의 당신이 있는것이다 . – 바바라 홀",
        "지금이야 말로 일할때다. 지금이야말로 싸울때다. 지금이야말로 나를 더 훌륭한 사람으로 만들때다 오늘 그것을 못하면 내일 그것을 할수있는가- 토마스 아켐피스",
        "모든것들에는 나름의 경이로움과 심지어 어둠과 침묵이 있고 , 내가 어떤 상태에 있더라도 나는 그속에서 만족하는 법을 배운다 -헬렌켈러",
        "작은 기회로 부터 종종 위대한 업적이 시작된다 -데모스테네스",
        "인생이란 학교에는 불행 이란 훌륭한 스승이 있다. 그 스승 때문에 우리는 더욱 단련되는 것이다. -프리체",
        "세상은 고통으로 가득하지만 그것을 극복하는 사람들로도 가득하다 – 헨렌켈러",
        "도저히 손댈 수가 없는 곤란에 부딪혔다면 과감하게 그 속으로 뛰어들라 . 그리하면 불가능하다고 생각했던 일이 가능해진다.",
        "용기있는 자로 살아라. 운이 따라주지 않는다면 용기 있는 가슴으로 불행에 맞서라. -키케로",
        "최고에 도달하려면 최저에서 시작하라. -P.시루스",
        "내 비장의 무기는 아직 손안에 있다 .그것은 희망이다 – 나폴레옹",
        "문제는 목적지에 얼마나 빨리 가느내가 아니라 그 목적지가 어디냐는 것이다. -메이벨 뉴컴버",
        "한 번 실패와 영원한 실패를 혼동하지 마라. -F.스콧 핏제랄드",
        "인간의 삶 전체는 단지 한 순간에 불과하다 . 인생을 즐기자 – 플루타르코스",
        "겨울이 오면 봄이 멀지 않으리 -셸리",
        "일하여 얻으라 . 그러면 운명의 바퀴를 붙들어 잡은것이다 -랄프 왈도 에머슨",
        "당신의 행복은 무엇이 당신의 영혼을 노래하게 하는가에 따라 결정된다. – 낸시 설리번",
        "자신이 해야 할 일을 결정하는 사람은 세상에서 단 한 사람, 오직 나 자신뿐이다. -오손 웰스-",
        "먹고 싶은것을 다 먹는 것은 그렇게 재미있지 않다 . 인생을 경계선 없이 살면 기쁨이 덜하다 . 먹고싶은대로 다 먹을 수있다면 먹고싶은 것을 먹는데 무슨 재미가 있겠나 – 톰행크스",
        "인생을 다시 산다면 다음번에는 더 많은 실수를 저지르리라 – 나딘 스테어",
        "절대 어제를 후회하지 마라 . 인생은 오늘의 나 안에 있고 내일은 스스로 만드는 것이다 -L.론허바드",
        "인생에서 원하는 것을 엇기 위한 첫번째 단계는 내가 무엇을 원하는지 결정하는 것이다 -벤스타인",
        "가난은 가난하다고 느끼는 곳에 존재한다 .- 에머슨",
        "삶이 그대를 속일지라도 슬퍼하거나 노하지 말아라 슬픈 날에 참고 견디라 . 즐거운 날은 오고야 말리니 마음은 미래를 바라느니 현재는 한없이 우울한것 모든건 하염없이 사라지나가 버리고 그리움이 되리니 – 푸쉬킨",
        "문제점을 찾지 말고 해결책을 찾으라 – 헨리포드",
        "우선 무엇이 되고자 하는가를 자신에게 말하라 그리고 해야 할일을 하라 -에픽토테스",
        "되찾을 수 없는게 세월이니 시시한 일에 시간을 낭비하지 말고 순간순간을 후회 없이 잘 살아야 한다. -루소",
        "인생에 뜻을 세우는데 있어 늦은 때라곤 없다 – 볼드윈",
        "도중에 포기하지 말라. 망설이지 말라. 최후의 성공을 거둘 때까지 밀고 나가자. – 헨리포드",
        "네 자신의 불행을 생각하지 않게 되는 가장 좋은 방법은 일에 몰두하는 것이다. -베토벤",
        "우리는 두려움의 홍수에 버티기 위해서 끊임없이 용기의 둑을 쌓아야 한다. -마틴 루터 킹",
        "직접 눈으로 본 일도 오히려 참인지 아닌지 염려스러운데 더구나 등뒤에서 남이 말하는 것이야 어찌 이것을 깊이 믿을 수 있으랴? -명심보감-",
        "이미끝나버린 일을 후회하기 보다는 하고 싶었던 일들을 하지못한 것을 후회하라. – 탈무드",
        "실패는 잊어라 그러나 그것이 준 교훈은 절대 잊으면 안된다. -하버트 개서",
        "내가 헛되이 보낸 오늘은 어제 죽어간 이들이 그토록 바라던 하루이다 단 하루면 인간적인 모든 것을 멸망시킬수도 다시 소생시킬수도 있다. -소포클레스",
        "성공으로 가는 엘리베이터는 고장입니다. 당신은 계단을 이용해야만 합니다. 한계단 한계단씩 – 조 지라드",
        "길을 잃는 다는 것은 곧 길을 알게 된다는 것이다. – 동아프리카속담",
        "삶을 사는 데는 단 두가지 방법이 있다. 하나는 기적이 전혀 없다고 여기는 것이고 또 다른 하나는 모든 것이 기적이라고 여기는방식이다. – 알베르트 아인슈타인",
    ]

    return random.choice(lst)
