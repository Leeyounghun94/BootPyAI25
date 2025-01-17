from fastapi import FastAPI     # FastAPI : 파이썬 웹 개발 API 를 이용해서 JSON처리를 한다.
from pydantic import BaseModel  # 유효성 검사용 판다틱
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
# BaseHTTPMiddleware 는 요청과 응답 사이에 특정 작업 수행
#   미들웨어는 모든 요청에 대해 실행이 되고, 요청을 처리하기 전에 응답을 반환하기 전에 특정 작업을 수행할 수 있다.
#       예를 들어, 로그인(세션), 인증, cors 처리, 압축 등 . . .

import logging  # 로그 출력용

from starlette.requests import Request
from starlette.responses import Response

app = FastAPI(      # 생성자를 통해서 PostMan을 대체하는 문서화 툴이 내장되어 있다.
    title="MBC AI 프로젝트 TEST",
    description="파이썬과 자바 부트를 연동한 AI 앱",
    version="1.0.0",
    docs_url=None,            # http://localhost:8001/docs 로 입력하면 FastAPI 내장된 포스트맨이 나오는데 별로 추천하지 않는다(테스트하고 None 처리해야한다(보안 위협))
    redoc_url=None              # http://localhost:8001/redoc 내장된 페이지가 열리는데 여기도 마찬가지.(테스트 후 보안상 None 처리해야 한다.)
                                    # 결론, 내장된 툴 쓸꺼면 테스트 후 None 처리, 아니면 PostMan 활용
)           # FastAPI 객체 생성하여 app 변수에 넣는다.


class LoggingMiddleware(BaseHTTPMiddleware) :   # 로그를 콘솔에 출력하는 용도.
    logging.basicConfig(level=logging.INFO)     # 로그 출력 추가
    async def dispatch(self, request, call_next):
        logging.info(f"Req: {request.method}{request.url}")
        response = await call_next(request)
        logging.info(f"Status Code : {response.status_code}")
        return response
app.add_middleware(LoggingMiddleware)
# 모든 요청에 대해 로그를 남기는 미들웨어 클래스를 사용한다.


class Item(BaseModel):  # item 객체 생성(BaseModel : 객체 연결(상속 개념)
    name : str                  # 필드1 : 상품명(문자)
    description : str = None    # 필드2 : 상품 설명(문자(null))
    price : float               # 필드3 : 가격(실수)
    tax : float = None          # 필드4 : 세금(실수(null))

    # 컨트롤러 검증은 PostMan으로 활용해봤는데 내장된 백검증 툴도 있다.

@app.get("/")   # http://ip주소:포트번호/ (루트컨텍스트)
async def read_root():
    return {"HELLO" : "World"}

@app.post("/items/")    # POST 방식 메서드용 응답
async def create_item(item: Item):      # 여기서, BaseModel은 데이터 모델링을 쉽게 도와주고 유효성 검사도 수행한다.
    # 잘못된 데이터가 들어오면 422 오류코드를 반환.
    return item

@app.get("/items/{item_id}")    # http://ip주소:포트/items/1
async def read_item(item_id: int, q:str = None):
    return {"item_id" : item_id, "q" : q}
    # item_id : 상품의 번호 -> 경로 매개변수
    # q : 쿼리 매개변수(기본값:None)