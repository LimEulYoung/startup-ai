from pydantic import BaseModel
from typing import List, Optional

class UserQuery(BaseModel):
    query: str
    limit: Optional[int] = 2

class AgenticSearchResult(BaseModel):
    query: str
    selected_regulations: List[str]
    classification_reason: str
    answer: str
    sources: List[str]
    reasoning: str
    relevant_sections: List[str]