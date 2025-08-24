from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import UserQuery, AgenticSearchResult, KakaoRequest, KakaoResponse, KakaoTemplate, KakaoOutput, KakaoSimpleText
from backend.agents.agent_system import RegulationAgentSystem
import os
import json
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        # OpenAI API 키가 환경변수에 설정되었는지 확인
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            regulation_agents = None
            return
            
        # OpenAI Agents SDK 기반 시스템 초기화
        regulation_agents = RegulationAgentSystem()
        print("RegulationAgentSystem initialized successfully with OpenAI Agents SDK")
    except Exception as e:
        print(f"Failed to initialize RegulationAgentSystem: {e}")
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
    """분류 테스트용 엔드포인트 (OpenAI Agents SDK에서는 자동 분류)"""
    if not regulation_agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        # OpenAI Agents SDK에서는 오케스트레이터가 자동으로 적절한 에이전트 선택
        result = await regulation_agents.search(query.query)
        return {
            "query": query.query, 
            "classification_method": "OpenAI Agents SDK 자동 분류",
            "selected_agents": result["sources"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/regulation-search")
async def search_regulations(query: UserQuery):
    if not regulation_agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        result = await regulation_agents.search(query.query)
        return AgenticSearchResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/kakao-chatbot", response_model=KakaoResponse)
async def kakao_chatbot(kakao_req: KakaoRequest):
    """카카오톡 챗봇 메인 엔드포인트 - GPT-4o-mini로 빠른 응답"""
    
    timestamp = datetime.now().isoformat()
    user_question = kakao_req.userRequest.utterance
    user_id = kakao_req.userRequest.user.id
    
    logger.info(f"[KAKAO CHATBOT] {timestamp} - User ID: {user_id}, Question: {user_question}")
    
    if not regulation_agents:
        return KakaoResponse(
            template=KakaoTemplate(
                outputs=[
                    KakaoOutput(
                        simpleText=KakaoSimpleText(
                            text="죄송합니다. 현재 시스템이 초기화되지 않았습니다. 잠시 후 다시 시도해주세요."
                        )
                    )
                ]
            )
        )
    
    try:
        # GPT-4o-mini로 직접 AI 처리 (빠른 응답 기대)
        result = await regulation_agents.search(user_question)
        answer = result.get("answer", "답변을 찾을 수 없습니다.")
        
        logger.info(f"[KAKAO CHATBOT] {timestamp} - AI response for user {user_id}: {answer[:100]}...")
        
        return KakaoResponse(
            template=KakaoTemplate(
                outputs=[
                    KakaoOutput(
                        simpleText=KakaoSimpleText(text=answer)
                    )
                ]
            )
        )
            
    except Exception as e:
        logger.error(f"[KAKAO CHATBOT] {timestamp} - Error: {e}")
        
        return KakaoResponse(
            template=KakaoTemplate(
                outputs=[
                    KakaoOutput(
                        simpleText=KakaoSimpleText(
                            text="죄송합니다. 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                        )
                    )
                ]
            )
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)