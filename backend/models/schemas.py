from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserQuery(BaseModel):
    query: str
    limit: Optional[int] = 2

class AgenticSearchResult(BaseModel):
    query: str
    selected_regulations: List[str]
    selected_agents: List[str]  # 새로 추가: 사용된 에이전트 이름들
    classification_reason: str
    answer: str
    sources: List[str]
    reasoning: str
    relevant_sections: List[str]

# 카카오톡 챗봇 스키마
class KakaoUser(BaseModel):
    id: str
    type: str
    properties: Dict[str, Any] = {}

class KakaoBlock(BaseModel):
    id: str
    name: str

class KakaoIntent(BaseModel):
    id: str
    name: str

class KakaoAction(BaseModel):
    name: str
    clientExtra: Optional[Any] = None
    params: Dict[str, Any] = {}
    id: str
    detailParams: Dict[str, Any] = {}

class KakaoUserRequest(BaseModel):
    timezone: str
    params: Dict[str, Any] = {}
    block: KakaoBlock
    utterance: str
    lang: Optional[str] = None
    user: KakaoUser

class KakaoBot(BaseModel):
    id: str
    name: str

class KakaoRequest(BaseModel):
    intent: KakaoIntent
    userRequest: KakaoUserRequest
    bot: KakaoBot
    action: KakaoAction

# 카카오톡 응답 스키마
class KakaoSimpleText(BaseModel):
    text: str

class KakaoOutput(BaseModel):
    simpleText: KakaoSimpleText

class KakaoTemplate(BaseModel):
    outputs: List[KakaoOutput]

class KakaoResponse(BaseModel):
    version: str = "2.0"
    template: KakaoTemplate