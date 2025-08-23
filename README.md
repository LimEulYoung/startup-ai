# 창업진흥원 규정 질의응답 챗봇

## 개요
창업진흥원의 규정에 대한 질의응답을 처리하는 에이전트 기반 챗봇 시스템입니다.
키워드 매칭이 아닌 AI 에이전트를 활용하여 정확하고 맥락적인 답변을 제공합니다.

## 시작하기

### 1. 환경 설정
```bash
# 가상환경 생성 (선택사항)
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
# 개발 서버 시작
python -m uvicorn backend.main:app --reload --port 8000

# 또는
uvicorn backend.main:app --reload --port 8000
```

서버가 시작되면 다음과 같은 메시지가 표시됩니다:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID] using StatReload
INFO:     Started server process [PID]
INFO:     Application startup complete.
```

## 테스트 방법

### 1. 웹 브라우저 테스트 (권장)
1. 브라우저에서 `http://localhost:8000/docs` 접속
2. FastAPI 자동 문서화 페이지가 열림
3. `POST /api/regulation-search` 섹션 클릭
4. "Try it out" 버튼 클릭
5. Request body에 테스트 질문 입력:
```json
{
  "query": "선정평가 수당을 2시간 했는데 얼마를 줘야해?"
}
```
6. "Execute" 버튼 클릭하여 결과 확인

### 2. curl 명령어 테스트
```bash
# 수당 관련 질문
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "선정평가 수당을 2시간 했는데 얼마를 줘야해?"}'

# 절차 관련 질문
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "창업기업 신청자격은?"}'

# 전문계약직 관련 질문
curl -X POST "http://localhost:8000/api/regulation-search" \
  -H "Content-Type: application/json" \
  -d '{"query": "전문계약직 가급 연봉은 얼마인가요?"}'
```

### 3. PowerShell 테스트 (Windows)
```powershell
# 수당 질문
Invoke-RestMethod -Uri 'http://localhost:8000/api/regulation-search' -Method Post -ContentType 'application/json' -Body '{"query": "선정평가 수당은 얼마인가요?"}'

# 절차 질문
Invoke-RestMethod -Uri 'http://localhost:8000/api/regulation-search' -Method Post -ContentType 'application/json' -Body '{"query": "창업기업 신청 절차는?"}'
```

### 4. 분류 테스트 (개발용)
분류 에이전트만 단독으로 테스트하고 싶을 때:
```bash
curl -X POST "http://localhost:8000/api/test-classification" \
  -H "Content-Type: application/json" \
  -d '{"query": "수당은 얼마인가요?"}'
```

## 응답 형식
```json
{
  "query": "선정평가 수당을 2시간 했는데 얼마를 줘야해?",
  "selected_regulations": ["창업사업화 지원사업 통합관리지침.txt"],
  "classification_reason": "에이전트 기반 분류",
  "answer": "평가·심사 수당은 시간당 10만원 이내입니다. 2시간이면 최대 20만원까지 지급 가능해요.",
  "sources": ["창업사업화 지원사업 통합관리지침.txt"],
  "reasoning": "에이전트 기반 생성",
  "relevant_sections": []
}
```

## 처리 가능한 규정
1. **중소기업창업 지원사업 운영요령**: 신청자격, 선정절차, 협약관리
2. **창업사업화 지원사업 통합관리지침**: 수당지급, 예산집행, 회계처리
3. **전문계약직 운영지침**: 채용, 급여, 연봉체계

## 기타 엔드포인트
- `GET /`: 시스템 상태 확인
- `GET /api/health`: 헬스체크
- `GET /api/regulations`: 로드된 규정 목록 조회

## 문제 해결
- **서버 시작 안됨**: OpenAI API 키 확인
- **응답이 없음**: 포트 8000이 사용 중인지 확인
- **에러 발생**: 터미널에서 에러 메시지 확인# startup-ai
