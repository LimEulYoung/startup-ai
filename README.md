# 창업진흥원 규정 질의응답 챗봇

## 개요
창업진흥원의 62개 규정에 대한 질의응답을 처리하는 AI 챗봇 시스템입니다.
**Upstage Solar-Pro2** AI 모델을 활용하여 정확하고 맥락적인 답변을 제공하며, 실시간 뉴스 서비스와 대화 메모리 기능을 지원합니다.

## 주요 기능
- 🤖 **Upstage Solar-Pro2** 모델 기반 정확한 규정 질의응답
- 📚 **62개 규정** 포괄적 지원 (감사규정, 여비규정, 보수규정, 인사규정 등)
- 📮 **실시간 뉴스** Google News RSS 연동
- 🧠 **대화 메모리** 사용자별 맥락 유지
- 💬 **카카오톡 챗봇** API 연동
- 🌐 **RESTful API** 제공

## 빠른 시작 (리눅스/맥OS)

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/startup-ai.git
cd startup-ai
```

### 2. 환경 설정
```bash
# Python 가상환경 생성
python3 -m venv .venv

# 가상환경 활성화
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3. 환경변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (API 키 설정)
nano .env
```

**.env 파일 내용:**
```bash
UPSTAGE_API_KEY=your_upstage_api_key_here
```

### 4. 서버 실행
```bash
# 프로덕션 서버 실행
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 개발 서버 실행 (자동 재시작)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

서버가 성공적으로 시작되면:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## API 사용 방법

### 1. 웹 브라우저 테스트 (권장)
```bash
# 브라우저에서 FastAPI 자동 문서화 페이지 접속
http://localhost:8000/docs
```

### 2. 규정 질의응답 API
```bash
# 수당 관련 질문
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "평가수당 2시간하면 얼마야?"}'

# 출장비 관련 질문  
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "대리가 부산 출장가면 숙박비 얼마받아?"}'

# 전문계약직 관련 질문
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "전문계약직 가급 연봉은?"}'

# 휴가 관련 질문
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "연차 며칠 줘?"}'
```

### 3. 뉴스 서비스 API
```bash
# 오늘의 창업진흥원 뉴스 조회
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "📮 오늘의 창업진흥원"}'
```

### 4. 카카오톡 챗봇 API
```bash
# 카카오톡 챗봇 형식으로 질문
curl -X POST "http://localhost:8000/api/kakao-chatbot" \
  -H "Content-Type: application/json" \
  -d '{
    "userRequest": {
      "utterance": "과장이 대전으로 2박3일 출장가면 얼마 받을 수 있어?"
    },
    "user": {
      "id": "test_user_123"
    }
  }'
```

## 응답 형식

### 웹 API 응답
```json
{
  "query": "평가수당 2시간하면 얼마야?",
  "answer": "평가·심사 수당은 시간당 10만원 이내입니다. 2시간이면 최대 20만원까지 지급 가능해요.",
  "total_time": "2.15초"
}
```

### 카카오톡 챗봇 응답
```json
{
  "version": "2.0",
  "template": {
    "outputs": [
      {
        "simpleText": {
          "text": "평가·심사 수당은 시간당 10만원 이내입니다. 2시간이면 최대 20만원까지 지급 가능해요."
        }
      }
    ]
  }
}
```

## 지원 규정 (62개)
- **감사 관련**: 감사규정, 감사규정 시행규칙
- **인사 관련**: 인사규정, 채용지침, 전문계약직 운영지침, 무기계약직 인사규칙
- **급여/수당**: 보수규정, 수당지급규칙, 연장근로수당지급 규칙
- **출장/여비**: 여비규정, 국외출장 관리지침
- **복무 관련**: 복무규정, 근무평정 규칙, 임원 복무 규정
- **사업 운영**: 중소기업창업 지원사업 운영요령, 창업사업화 지원사업 통합관리지침
- **기타**: 정관, 직제규정, 위임전결규정, 회계규정 등 47개 추가 규정

## API 엔드포인트
```
GET  /                         # 루트 - 시스템 정보
GET  /api/health              # 헬스체크  
GET  /api/regulations         # 로드된 규정 목록 조회
POST /api/regulation-search   # 메인 - AI 기반 규정 질의응답
POST /api/kakao-chatbot       # 카카오톡 챗봇 API
GET  /docs                    # FastAPI 자동 문서화
```

## 배포 (AWS/리눅스 서버)

### 1. 서버 환경 설정
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Python 및 필수 패키지 설치
sudo apt install python3 python3-pip python3-venv -y

# 프로젝트 클론
git clone https://github.com/your-username/startup-ai.git
cd startup-ai
```

### 2. 프로덕션 환경 설정
```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
nano .env  # UPSTAGE_API_KEY 설정
```

### 3. 서비스 실행
```bash
# 백그라운드 실행
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &

# 또는 systemd 서비스로 등록하여 관리
```

## 특별 명령어
- `📮 오늘의 창업진흥원`: 실시간 뉴스 조회 + 대화 이력 초기화
- `🌟 새로운 대화시작`: 대화 이력 초기화

## 기술 스택
- **Backend**: FastAPI
- **AI Model**: Upstage Solar-Pro2
- **Language**: Python 3.9+
- **Database**: JSON (대화 메모리)
- **External APIs**: Google News RSS

## 문제 해결
- **서버 시작 안됨**: UPSTAGE_API_KEY 환경변수 확인
- **응답이 없음**: 방화벽 및 포트 8000 사용 여부 확인  
- **메모리 에러**: conversation_memory.json 파일 권한 확인
- **뉴스 안나옴**: 인터넷 연결 및 Google News RSS 접근 확인

## 라이센스
MIT License

## 기여하기
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)  
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
