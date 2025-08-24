from pydantic import BaseModel
from typing import List, Optional

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