from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import UserQuery, AgenticSearchResult, KakaoRequest, KakaoResponse, KakaoTemplate, KakaoOutput, KakaoSimpleText
from backend.agents.agent_system import RegulationAgentSystem
import os
import json
import logging
import asyncio
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

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
active_callbacks = {}  # 진행 중인 콜백 요청 추적 {callback_url: start_time}


@app.on_event("startup")
async def startup_event():
    global regulation_agents
    
    try:
        # Upstage API 키가 환경변수에 설정되었는지 확인
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            print("Warning: UPSTAGE_API_KEY not found in environment variables")
            regulation_agents = None
            return
            
        # Upstage Solar-Pro2 기반 시스템 초기화
        regulation_agents = RegulationAgentSystem()
        print("RegulationAgentSystem initialized successfully with Upstage Solar-Pro2")
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


@app.post("/api/regulation-search")
async def search_regulations(query: UserQuery):
    if not regulation_agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")
    
    try:
        # 웹 API는 user_id 없이 호출 (메모리 기능 없음)
        result = await regulation_agents.search(query.query)
        return AgenticSearchResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/kakao-chatbot", response_model=KakaoResponse)
async def kakao_chatbot(kakao_req: KakaoRequest):
    """카카오톡 챗봇 메인 엔드포인트 - 콜백 기능 지원"""
    
    timestamp = datetime.now().isoformat()
    user_question = kakao_req.userRequest.utterance
    user_id = kakao_req.userRequest.user.id
    callback_url = kakao_req.userRequest.callbackUrl
    
    logger.info(f"[KAKAO CHATBOT] {timestamp} - User ID: {user_id}, Question: {user_question}")
    if callback_url:
        logger.info(f"[KAKAO CHATBOT] Callback URL detected")
    
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
    
    # 콜백 URL이 있으면 **즉시** 콜백 응답 후 백그라운드 처리  
    if callback_url:
        logger.info(f"[KAKAO CHATBOT] Callback mode - returning immediate response")
        
        # 응답 반환과 동시에 백그라운드 처리 예약
        def start_background_processing():
            asyncio.create_task(handle_callback_processing(callback_url, user_question, user_id, timestamp))
        
        # 응답 반환 직후 실행되도록 예약
        asyncio.get_event_loop().call_soon(start_background_processing)
        
        # **즉시** 콜백 응답 반환 (토큰 만료 방지)
        return KakaoResponse(
            version="2.0",
            useCallback=True
        )
    
    # 기존 동기 처리 (콜백 URL 없는 경우)
    try:
        result = await regulation_agents.search(user_question, user_id)
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


def is_valid_callback_url(callback_url: str) -> bool:
    """콜백 URL 유효성 검사"""
    if not callback_url:
        return False
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(callback_url)
        
        # HTTPS 및 카카오 도메인 기본 체크
        return (parsed.scheme == "https" and 
                "kakao" in parsed.netloc.lower())
        
    except Exception as e:
        logger.error(f"[CALLBACK] URL validation error: {e}")
        return False


def create_error_response(message: str) -> KakaoResponse:
    """에러 응답 생성"""
    return KakaoResponse(
        template=KakaoTemplate(
            outputs=[
                KakaoOutput(
                    simpleText=KakaoSimpleText(text=message)
                )
            ]
        )
    )


async def send_callback_response(callback_url: str, response_data: dict, max_retries: int = 1) -> bool:
    """콜백 응답 전송 (카카오 콜백 토큰은 1회성이므로 재시도 없음)"""
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                callback_url,
                json=response_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                logger.info(f"[CALLBACK] Success: {response.status_code}")
                return True
            else:
                logger.error(f"[CALLBACK] Failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"[CALLBACK] Network error: {e}")
        return False


async def send_timeout_response(callback_url: str):
    """타임아웃 응답 전송"""
    timeout_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "처리 시간이 초과되었습니다. 다시 시도해주세요."
                    }
                }
            ]
        }
    }
    
    await send_callback_response(callback_url, timeout_response, max_retries=1)


async def send_error_response(callback_url: str, error_message: str):
    """에러 응답 전송"""
    error_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": error_message
                    }
                }
            ]
        }
    }
    
    await send_callback_response(callback_url, error_response, max_retries=1)


async def handle_callback_processing(callback_url: str, user_question: str, user_id: str, timestamp: str):
    """콜백 응답 후 실제 AI 처리를 담당하는 함수"""
    
    # 콜백 URL 유효성 검사 및 중복 방지
    if not is_valid_callback_url(callback_url):
        logger.warning(f"[CALLBACK] Invalid callback URL: {callback_url}")
        await send_error_response(callback_url, "잘못된 콜백 요청입니다.")
        return
    
    if callback_url in active_callbacks:
        logger.warning(f"[CALLBACK] Duplicate callback URL: {callback_url}")
        await send_error_response(callback_url, "이미 처리 중인 요청입니다.")
        return
    
    # 콜백 요청 등록 (응답 후 처리)
    callback_start_time = time.time()
    active_callbacks[callback_url] = callback_start_time
    logger.info(f"[CALLBACK] Processing: {user_question[:50]}...")
    
    # 실제 AI 처리 수행
    await process_callback_request(callback_url, user_question, user_id)


async def process_callback_request(callback_url: str, user_question: str, user_id: str):
    """백그라운드에서 AI 처리를 수행하고 콜백 URL로 응답을 전송"""
    start_time = time.time()
    
    try:
        callback_registered_time = active_callbacks.get(callback_url, 0)
        elapsed_time = time.time() - callback_registered_time
        
        # 타임아웃 검사 (50초 제한 - 여유분 확보)
        if elapsed_time > 50:
            logger.warning(f"[CALLBACK] Timeout exceeded: {elapsed_time:.2f}s")
            await send_timeout_response(callback_url)
            return
        
        # AI 처리 수행
        result = await regulation_agents.search(user_question, user_id)
        answer = result.get("answer", "답변을 찾을 수 없습니다.")
        
        # 표준 카카오톡 응답 포맷
        callback_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": answer
                        }
                    }
                ]
            }
        }
        
        # 콜백 URL로 전송 (1회만 - 카카오 콜백 토큰은 1회성)
        success = await send_callback_response(callback_url, callback_response, max_retries=1)
        
        if success:
            processing_time = time.time() - start_time
            logger.info(f"[CALLBACK] Success: {answer[:50]}... (Time: {processing_time:.2f}s)")
        else:
            logger.error(f"[CALLBACK] Failed to send response")
                
    except Exception as e:
        logger.error(f"[CALLBACK] Error: {e}")
        await send_error_response(callback_url, "처리 중 오류가 발생했습니다.")
    
    finally:
        # 콜백 요청 완료 후 정리
        if callback_url in active_callbacks:
            del active_callbacks[callback_url]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)