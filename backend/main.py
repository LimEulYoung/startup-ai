from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import UserQuery, AgenticSearchResult
from backend.agents.agent_system import RegulationAgentSystem
import os

app = FastAPI(
    title="창업진흥원 규정 질의응답 API",
    description="에이전트 기반 창업진흥원 규정 검색 및 질의응답 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수
regulation_agents = None

@app.on_event("startup")
async def startup_event():
    global regulation_agents
    
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        regulation_agents = RegulationAgentSystem(api_key=api_key)
    except Exception as e:
        regulation_agents = None

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "창업진흥원 규정 질의응답 API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/regulations")
async def get_regulations():
    if not regulation_agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    return {"regulations": list(regulation_agents.regulations.keys())}

@app.post("/api/test-classification")
async def test_classification(query: UserQuery):
    """분류 테스트용 엔드포인트"""
    if not regulation_agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        selected_file = regulation_agents._classification_agent(query.query)
        return {"query": query.query, "selected_file": selected_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/regulation-search")
async def search_regulations(query: UserQuery):
    if not regulation_agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        result = regulation_agents.search(query.query)
        return AgenticSearchResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)