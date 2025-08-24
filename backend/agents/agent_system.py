from openai import OpenAI
import os
import json
from typing import Dict, List


class RegulationAgentSystem:
    def __init__(self):
        # OpenAI API 키 설정
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        self.regulations = self._load_regulations()
    
    def _load_regulations(self) -> Dict[str, str]:
        """규정 파일들을 로드"""
        regs = {}
        data_dir = "data"
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.txt'):
                    with open(f"{data_dir}/{filename}", 'r', encoding='utf-8') as f:
                        regs[filename] = f.read()
        return regs
    
    def _classification_agent(self, user_query: str) -> str:
        """규정 분류 에이전트"""
        system_prompt = """당신은 창업진흥원 규정 분류 전문가입니다.
사용자 질문을 분석해서 가장 적합한 규정을 선택하세요.

다음 14개 규정 중에서 선택하세요:

1. startup_support_agent (중소기업창업 지원사업 운영요령)
- 창업지원사업의 기본 운영체계와 절차를 규정
- 사업 신청자격, 선정기준, 협약체결 절차가 포함됨
- 창업기업 및 예비창업자의 지원 대상 기준 명시
- 사업 진행 과정에서의 관리감독 방법 규정
- 사업 완료 후 성과관리 및 사후관리 절차 포함
- 주요 키워드: 신청, 자격, 절차, 협약, 관리

2. budget_management_agent (창업사업화 지원사업 통합관리지침)
- 창업사업화 지원사업의 예산 집행과 회계처리 기준
- 각종 수당 및 인건비 지급 기준과 한도액 명시
- 평가위원, 멘토, 전문가에 대한 수당 지급 규정
- 사업비 사용 범위와 집행 절차 규정
- 정산 및 회계감사 관련 사항 포함
- 주요 키워드: 수당, 비용, 지급, 예산, 회계

3. contract_employee_agent (전문계약직 운영지침)
- 창업진흥원 전문계약직의 인사관리 규정
- 채용자격, 채용절차, 임기 및 신분에 관한 사항
- 급여체계, 연봉 책정기준, 성과급 규정
- 근무평정, 해임 사유, 퇴직금 등 처우 규정
- 등급별(가급~마급) 자격요건과 보수기준 명시
- 주요 키워드: 전문계약직, 채용, 급여, 연봉, 등급

4. delegation_agent (위임전결규정)
- 창업진흥원 내부 업무처리의 권한과 절차를 규정
- 직위별(원장, 본부장/단장, 부서장) 위임전결사항 명시
- 사업, 예산, 복무, 민원, 계약, 인사, 총무, 감사 등 전 업무영역 포괄
- 업무의 신속성과 효율성 향상을 위한 권한 분담 체계
- 각종 승인, 결재, 보고 등의 전결권한 기준 제시
- 주요 키워드: 권한, 결재, 승인, 위임전결

5. overseas_trip_agent (국외출장 등에 대한 관리지침)
- 창업진흥원 임직원의 국외출장 및 파견에 관한 규정
- 국외출장 허가절차, 심사위원회 구성 및 운영방법
- 출장 금지사항, 선물수령 신고, 항공마일리지 관리
- 출장비 지급기준, 결과보고서 작성 및 공개 의무
- 출장 준수사항 및 예산낭비 방지를 위한 규정
- 주요 키워드: 국외출장, 해외출장, 허가, 심사

6. travel_expense_agent (여비규정)
- 창업진흥원 임직원의 국내외 출장 여비에 관한 규정
- 국내여비(시내출장, 시외출장), 국외여비, 기타여비 구분
- 운임, 체재비(일비, 식비, 숙박비), 준비금 지급기준
- 직급별, 출장지역별 세부 지급 기준 및 한도액
- 여비 계산방법, 정산절차, 감액사유 등 운영규정
- 주요 키워드: 여비, 일비, 숙박비, 출장비, 체재비

7. salary_agent (보수규정)
- 창업진흥원 임직원의 보수(연봉, 급여, 수당) 전반에 관한 규정
- 기본연봉, 성과연봉, 부가급여의 구체적 지급기준과 금액
- 직급별(1가급~6급) 및 기준별(기준1~30) 세부 연봉표 포함
- 각종 수당(직책수당, 출납수당, 전문관수당, 안전관리선임수당 등) 지급기준
- 연장근로수당, 연차휴가수당, 휴업수당 등 특별 수당 규정
- 주요 키워드: 연봉, 기본급, 성과급, 직급별 급여

8. work_regulation_agent (복무규정)
- 창업진흥원 임직원의 복무에 관한 규정
- 직원의 준수사항, 출근시간, 근무시간, 휴가제도
- 연차휴가, 병가, 특별휴가(경조사, 출산, 난임치료 등) 규정
- 시간외근무, 휴일근무, 유연근무, 선택적 근로시간제
- 출장, 휴직, 복무위반 처분기준
- 주요 키워드: 근무시간, 휴가, 연차, 복무, 출근

9. position_agent (직위운용규칙)
- 창업진흥원 직원의 직위운영 및 호칭에 관한 규정
- 직위구분: 선임부장, 부장, 차장, 과장, 대리, 주임, 사원
- 업무특성별 호칭 체계 (경영 및 일반창업 지원, 조사연구, 운전직)
- 직급별, 직책별, 임금피크제 적용 시 호칭 기준
- 직위 임용 및 겸직 직책 부여 절차
- 주요 키워드: 직위, 호칭, 직급, 직책

10. organization_agent (직제규정)
- 창업진흥원의 직제, 조직, 업무분장 및 정원에 관한 규정
- 조직편제: 4개 본부, 1개 단, 대외협력팀, 감사팀으로 구성
- 각 부서별(기획조정실, 정책개발팀, 미래인재팀 등) 업무분장 상세 규정
- 직급별(1가급~6급) 직위·직책 기준 및 정원표 포함
- 원장, 본부장, 단장, 부서장, 파트장의 직무 및 권한 규정
- 주요 키워드: 조직, 부서, 본부, 팀, 업무분장, 정원

11. recruitment_agent (채용 지침)
- 창업진흥원 직원 신규채용에 관한 세부 규정
- 채용계획 수립, 채용절차, 합격자 결정 기준
- 채용공정성 관리, 평가위원회 운영, 검증위원회 운영
- 부정행위자 처리, 친인척 채용공개, 채용전문업체 위탁
- 시용기간 중 근무평가 및 본채용 절차
- 주요 키워드: 채용, 면접, 전형, 합격, 공정성

12. youth_intern_agent (청년인턴 운영지침)
- 창업진흥원 청년인턴의 채용 및 운영에 관한 규정
- 청년인턴 자격요건, 채용절차, 계약기간, 근로조건
- 보수체계(기본급여, 부가급여), 휴가제도, 멘토링 운영
- 평가 및 우수인턴 선발, 취업 경쟁력 강화 교육
- 관리부서 운영 방안 및 청년일경험사업 가이드라인 반영
- 주요 키워드: 청년인턴, 인턴, 멘토링, 청년

13. employment_rule_agent (취업규칙)
- 창업진흥원 근로자의 채용, 복무 및 근로조건에 관한 규정
- 근로계약, 시용기간, 근로시간, 휴게시간, 휴가제도
- 임금계산, 승급, 상여금, 퇴직금 등 급여 관련 규정
- 복무의무, 출근결근, 안전보건, 재해보상, 남녀평등
- 성희롱 예방, 고충처리, 교육 및 복리후생 제도
- 주요 키워드: 근로조건, 근로계약, 시용기간, 안전보건

14. retirement_pay_agent (퇴직금 지급 규정)
- 창업진흥원 임원 및 직원의 퇴직급여 지급에 관한 규정
- 퇴직금 및 퇴직연금 지급대상, 지급기준, 계속근로기간 계산
- 임원 퇴직금의 감액 지급 사유 및 절차
- 명예퇴직수당 지급 기준과 제외 사유
- 퇴직급여의 수령자, 지급시기, 권리 소멸 규정
- 주요 키워드: 퇴직금, 퇴직급여, 명예퇴직수당, 계속근로기간

사용자 질문의 핵심 의도를 파악해서 다음 중 하나만 답변하세요:
- 운영요령
- 통합관리지침  
- 전문계약직지침
- 위임전결규정
- 국외출장지침
- 여비규정
- 보수규정
- 복무규정
- 직위운용규칙
- 직제규정
- 채용지침
- 청년인턴지침
- 취업규칙
- 퇴직금규정"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"사용자 질문: {user_query}"}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            result = response.choices[0].message.content.strip()
            
            # 파일명 매핑
            regulation_mapping = {
                "통합관리지침": "창업사업화 지원사업 통합관리지침.txt",
                "전문계약직지침": "전문계약직 운영지침.txt", 
                "위임전결규정": "위임전결규정.txt",
                "국외출장지침": "국외출장 등에 대한 관리지침.txt",
                "여비규정": "여비규정.txt",
                "보수규정": "보수규정.txt",
                "복무규정": "복무규정.txt",
                "직위운용규칙": "직위운용규칙.txt",
                "직제규정": "직제규정.txt",
                "채용지침": "채용 지침.txt",
                "청년인턴지침": "청년인턴 운영지침.txt",
                "취업규칙": "취업규칙.txt",
                "퇴직금규정": "퇴직금 지급 규정.txt"
            }
            
            # 매핑에서 찾기
            for key, filename in regulation_mapping.items():
                if key in result:
                    if filename in self.regulations:
                        return filename
            
            # 기본값: 운영요령
            return "중소기업창업 지원사업 운영요령(중소벤처기업부고시)(제2024-101호)(20241206).txt"
                    
        except Exception:
            # 에러 시 기본 선택 (운영요령)
            return "중소기업창업 지원사업 운영요령(중소벤처기업부고시)(제2024-101호)(20241206).txt"
    
    def _response_agent(self, user_query: str, regulation_file: str) -> str:
        """답변 생성 에이전트"""
        regulation_content = self.regulations[regulation_file]
        
        # 직급 정보 추가
        job_grade_info = """
직급 정보:
- 3급: 차장
- 4급: 과장  
- 5급: 주임 또는 대리
- 6급: 사원
- 팀장: 1(나)급, 1(가)급, 또는 2급 직원 중 하나
"""
        
        system_prompt = f"""당신은 창업진흥원 규정 질의응답 전문가입니다.
주어진 규정을 바탕으로 사용자 질문에 정확하고 간결한 답변을 제공하세요.

답변 규칙:
1. 반드시 한 줄로 연속된 텍스트로만 답변 (줄바꿈, 리스트, 구분자 금지)
2. 카카오톡 메신저에서 사용할 것이므로 줄바꿈 없는 일반 텍스트만 사용
3. 불렛포인트(-), 번호매기기(1.), 줄바꿈(\\n) 절대 금지
4. 질문에 정확히 대응하는 내용만 답변
5. 수당/금액 질문이면 구체적 수치와 간단한 설명을 한 문장으로
6. 카카오톡 대화하듯 친근하고 자연스럽게
7. 모든 정보를 쉼표나 접속사로 연결하여 하나의 연속된 문장으로 구성

{job_grade_info}"""

        user_message = f"""사용자 질문: {user_query}

관련 규정:
{regulation_content[:45000]}

위 규정을 참고해서 질문에 답변해주세요."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "답변 생성 중 오류가 발생했습니다."
    
    async def search(self, user_query: str) -> dict:
        """전체 에이전트 시스템 실행"""
        try:
            # 1단계: 분류 에이전트 (빠른 응답)
            selected_file = self._classification_agent(user_query)
            
            # 2단계: 답변 생성 에이전트 (빠른 응답)
            answer = self._response_agent(user_query, selected_file)
            
            return {
                "query": user_query,
                "selected_regulations": [selected_file.replace('.txt', '')],
                "selected_agents": ["simple_classification_agent", "simple_response_agent"],
                "classification_reason": "단순 OpenAI API 기반 분류",
                "answer": answer,
                "sources": [selected_file.replace('.txt', '')],
                "reasoning": "단순 OpenAI API 기반 생성",
                "relevant_sections": []
            }
            
        except Exception as e:
            return {
                "query": user_query,
                "selected_regulations": [],
                "selected_agents": [],
                "classification_reason": "오류 발생",
                "answer": "오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                "sources": [],
                "reasoning": str(e),
                "relevant_sections": []
            }
    
    # 기존 API 호환성을 위한 동기 래퍼
    def search_sync(self, user_query: str) -> dict:
        """동기 버전의 search 메서드"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.search(user_query))