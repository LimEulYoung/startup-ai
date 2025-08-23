from openai import OpenAI
import os
import json

class RegulationAgentSystem:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.regulations = self._load_regulations()
    
    def _load_regulations(self):
        regs = {}
        for filename in os.listdir("data"):
            if filename.endswith('.txt'):
                with open(f"data/{filename}", 'r', encoding='utf-8') as f:
                    regs[filename] = f.read()
        return regs
    
    def _classification_agent(self, user_query: str) -> str:
        """규정 분류 에이전트"""
        system_prompt = """당신은 창업진흥원 규정 분류 전문가입니다.
사용자 질문을 분석해서 가장 적합한 규정을 선택하세요.

다음 규정 중에서 선택하세요:

1. 중소기업창업 지원사업 운영요령
- 창업지원사업의 기본 운영체계와 절차를 규정
- 사업 신청자격, 선정기준, 협약체결 절차가 포함됨
- 창업기업 및 예비창업자의 지원 대상 기준 명시
- 사업 진행 과정에서의 관리감독 방법 규정
- 사업 완료 후 성과관리 및 사후관리 절차 포함
- 주요 내용: 누가 신청할 수 있는지, 어떤 절차로 진행되는지, 어떻게 관리되는지

2. 창업사업화 지원사업 통합관리지침  
- 창업사업화 지원사업의 예산 집행과 회계처리 기준
- 각종 수당 및 인건비 지급 기준과 한도액 명시
- 평가위원, 멘토, 전문가에 대한 수당 지급 규정
- 사업비 사용 범위와 집행 절차 규정
- 정산 및 회계감사 관련 사항 포함
- 주요 내용: 돈을 얼마나 줄 수 있는지, 어떤 비용을 쓸 수 있는지, 수당은 얼마인지

3. 전문계약직 운영지침
- 창업진흥원 전문계약직의 인사관리 규정
- 채용자격, 채용절차, 임기 및 신분에 관한 사항
- 급여체계, 연봉 책정기준, 성과급 규정
- 근무평정, 해임 사유, 퇴직금 등 처우 규정
- 등급별(가급~마급) 자격요건과 보수기준 명시
- 주요 내용: 전문계약직 채용, 급여, 근무조건, 연봉은 얼마인지

4. 위임전결규정
- 창업진흥원 내부 업무처리의 권한과 절차를 규정
- 직위별(원장, 본부장/단장, 부서장) 위임전결사항 명시
- 사업, 예산, 복무, 민원, 계약, 인사, 총무, 감사 등 전 업무영역 포괄
- 업무의 신속성과 효율성 향상을 위한 권한 분담 체계
- 각종 승인, 결재, 보고 등의 전결권한 기준 제시
- 주요 내용: 누가 어떤 업무를 결정할 권한이 있는지, 결재 절차는 어떻게 되는지

5. 국외출장 등에 대한 관리지침
- 창업진흥원 임직원의 국외출장 및 파견에 관한 규정
- 국외출장 허가절차, 심사위원회 구성 및 운영방법
- 출장 금지사항, 선물수령 신고, 항공마일리지 관리
- 출장비 지급기준, 결과보고서 작성 및 공개 의무
- 출장 준수사항 및 예산낭비 방지를 위한 규정
- 주요 내용: 국외출장 절차, 출장비, 허가기준, 심사방법

6. 여비규정
- 창업진흥원 임직원의 국내외 출장 여비에 관한 규정
- 국내여비(시내출장, 시외출장), 국외여비, 기타여비 구분
- 운임, 체재비(일비, 식비, 숙박비), 준비금 지급기준
- 직급별, 출장지역별 세부 지급 기준 및 한도액
- 여비 계산방법, 정산절차, 감액사유 등 운영규정
- 주요 내용: 출장여비 얼마인지, 일비 숙박비 기준, 여행경비

7. 보수규정
- 창업진흥원 임직원의 보수(연봉, 급여, 수당) 전반에 관한 규정
- 기본연봉, 성과연봉, 부가급여의 구체적 지급기준과 금액
- 직급별(1가급~6급) 및 기준별(기준1~30) 세부 연봉표 포함
- 각종 수당(직책수당, 출납수당, 전문관수당, 안전관리선임수당 등) 지급기준
- 연장근로수당, 연차휴가수당, 휴업수당 등 특별 수당 규정
- 주요 내용: 연봉이 얼마인지, 급여체계, 각종 수당 금액

8. 복무규정
- 창업진흥원 임직원의 복무에 관한 규정
- 직원의 준수사항, 출근시간, 근무시간, 휴가제도
- 연차휴가, 병가, 특별휴가(경조사, 출산, 난임치료 등) 규정
- 시간외근무, 휴일근무, 유연근무, 선택적 근로시간제
- 출장, 휴직, 복무위반 처분기준
- 주요 내용: 근무시간, 휴가일수, 근무규칙, 출결관리

9. 직위운용규칙
- 창업진흥원 직원의 직위운영 및 호칭에 관한 규정
- 직위구분: 선임부장, 부장, 차장, 과장, 대리, 주임, 사원
- 업무특성별 호칭 체계 (경영 및 일반창업 지원, 조사연구, 운전직)
- 직급별, 직책별, 임금피크제 적용 시 호칭 기준
- 직위 임용 및 겸직 직책 부여 절차
- 주요 내용: 직위 호칭, 직급 체계, 직책 호칭

10. 직제규정
- 창업진흥원의 직제, 조직, 업무분장 및 정원에 관한 규정
- 조직편제: 4개 본부, 1개 단, 대외협력팀, 감사팀으로 구성
- 각 부서별(기획조정실, 정책개발팀, 미래인재팀 등) 업무분장 상세 규정
- 직급별(1가급~6급) 직위·직책 기준 및 정원표 포함
- 원장, 본부장, 단장, 부서장, 파트장의 직무 및 권한 규정
- 주요 내용: 조직구조, 부서별 업무, 직급체계, 정원, 조직도

11. 채용 지침
- 창업진흥원 직원 신규채용에 관한 세부 규정
- 채용계획 수립, 채용절차, 합격자 결정 기준
- 채용공정성 관리, 평가위원회 운영, 검증위원회 운영
- 부정행위자 처리, 친인척 채용공개, 채용전문업체 위탁
- 시용기간 중 근무평가 및 본채용 절차
- 주요 내용: 채용절차, 심사기준, 면접전형, 합격자 결정, 공정성 관리

12. 청년인턴 운영지침
- 창업진흥원 청년인턴의 채용 및 운영에 관한 규정
- 청년인턴 자격요건, 채용절차, 계약기간, 근로조건
- 보수체계(기본급여, 부가급여), 휴가제도, 멘토링 운영
- 평가 및 우수인턴 선발, 취업 경쟁력 강화 교육
- 관리부서 운영 방안 및 청년일경험사업 가이드라인 반영
- 주요 내용: 청년인턴 채용, 급여, 근무조건, 평가, 멘토링

13. 취업규칙
- 창업진흥원 근로자의 채용, 복무 및 근로조건에 관한 규정
- 근로계약, 시용기간, 근로시간, 휴게시간, 휴가제도
- 임금계산, 승급, 상여금, 퇴직금 등 급여 관련 규정
- 복무의무, 출근결근, 안전보건, 재해보상, 남녀평등
- 성희롱 예방, 고충처리, 교육 및 복리후생 제도
- 주요 내용: 근로조건, 취업규칙, 근무시간, 휴가, 급여, 복무

14. 퇴직금 지급 규정
- 창업진흥원 임원 및 직원의 퇴직급여 지급에 관한 규정
- 퇴직금 및 퇴직연금 지급대상, 지급기준, 계속근로기간 계산
- 임원 퇴직금의 감액 지급 사유 및 절차
- 명예퇴직수당 지급 기준과 제외 사유
- 퇴직급여의 수령자, 지급시기, 권리 소멸 규정
- 주요 내용: 퇴직금 얼마인지, 퇴직급여 계산법, 지급 조건

사용자 질문의 핵심 의도를 파악해서 다음 중 하나만 답변하세요:
- 운영요령
- 통합관리지침  
- 전문계약직지침
- 위임전결규정
- 국외출장관리지침
- 여비규정
- 보수규정
- 복무규정
- 직위운용규칙
- 직제규정
- 채용지침
- 청년인턴운영지침
- 취업규칙
- 퇴직금지급규정"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"사용자 질문: {user_query}"}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            
            # 파일명 매핑
            if "통합관리지침" in result:
                return "창업사업화 지원사업 통합관리지침.txt"
            elif "전문계약직지침" in result or "전문계약직" in result:
                return "전문계약직 운영지침.txt"
            elif "위임전결규정" in result or "위임전결" in result:
                return "위임전결규정.txt"
            elif "국외출장관리지침" in result or "국외출장" in result:
                return "국외출장 등에 대한 관리지침.txt"
            elif "여비규정" in result or "여비" in result or "출장여비" in result or "일비" in result or "숙박비" in result:
                return "여비규정.txt"
            elif "보수규정" in result or "연봉" in result or "급여" in result or "기본연봉" in result or "성과연봉" in result:
                return "보수규정.txt"
            elif "복무규정" in result or "복무" in result or "근무시간" in result or "휴가" in result or "연차" in result:
                return "복무규정.txt"
            elif "직위운용규칙" in result or "직위" in result or "호칭" in result:
                return "직위운용규칙.txt"
            elif "직제규정" in result or "조직" in result or "업무분장" in result or "정원" in result or "본부" in result or "팀" in result or "부서" in result:
                return "직제규정.txt"
            elif "채용지침" in result or "채용" in result or "신규채용" in result or "면접" in result or "서류전형" in result or "합격자" in result or "평가위원" in result or "공정성" in result:
                return "채용 지침.txt"
            elif "청년인턴운영지침" in result or "청년인턴" in result or "인턴" in result or "멘토링" in result or "청년" in result:
                return "청년인턴 운영지침.txt"
            elif "취업규칙" in result or "근로조건" in result or "근로계약" in result or "시용기간" in result or "근로시간" in result or "복무의무" in result or "출근" in result or "결근" in result or "지각" in result or "조퇴" in result or "휴게시간" in result or "임금계산" in result or "상여금" in result or "안전보건" in result or "재해보상" in result or "성희롱" in result or "고충처리" in result:
                return "취업규칙.txt"
            elif "퇴직금지급규정" in result or "퇴직금" in result or "퇴직급여" in result or "퇴직연금" in result or "명예퇴직수당" in result or "계속근로기간" in result or "평균임금" in result or "기준급여" in result or "확정급여형" in result or "확정기여형" in result or "DB" in result or "DC" in result:
                return "퇴직금 지급 규정.txt"
            else:
                return "중소기업창업 지원사업 운영요령(중소벤처기업부고시)(제2024-101호)(20241206).txt"
                    
        except Exception:
            # 에러 시 기본 선택 (운영요령)
            return "중소기업창업 지원사업 운영요령(중소벤처기업부고시)(제2024-101호)(20241206).txt"
    
    def _response_agent(self, user_query: str, regulation_file: str) -> str:
        """답변 생성 에이전트"""
        regulation_content = self.regulations[regulation_file]
        
        system_prompt = """당신은 창업진흥원 규정 질의응답 전문가입니다.
주어진 규정을 바탕으로 사용자 질문에 정확하고 간결한 답변을 제공하세요.

답변 규칙:
1. 질문에 정확히 대응하는 내용만 답변
2. 수당 관련 질문이면 금액만, 절차 질문이면 절차만  
3. 카카오톡 대화하듯 친근하게
4. 구체적인 수치나 기준 포함
5. 2-3문장으로 간단히

직급 정보:
- 3급: 차장
- 4급: 과장  
- 5급: 주임 또는 대리
- 6급: 사원
- 팀장: 1(나)급, 1(가)급, 또는 2급 직원 중 하나"""

        user_message = f"""사용자 질문: {user_query}

관련 규정:
{regulation_content[:50000]}

위 규정을 참고해서 질문에 답변해주세요."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
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
    
    def search(self, user_query: str):
        """전체 에이전트 시스템 실행"""
        try:
            # 1단계: 분류 에이전트
            selected_file = self._classification_agent(user_query)
            
            # 2단계: 답변 생성 에이전트  
            answer = self._response_agent(user_query, selected_file)
            
            return {
                "query": user_query,
                "selected_regulations": [selected_file],
                "classification_reason": "에이전트 기반 분류",
                "answer": answer,
                "sources": [selected_file],
                "reasoning": "에이전트 기반 생성",
                "relevant_sections": []
            }
            
        except Exception as e:
            return {
                "query": user_query,
                "selected_regulations": [],
                "classification_reason": "오류 발생",
                "answer": "오류가 발생했습니다.",
                "sources": [],
                "reasoning": str(e),
                "relevant_sections": []
            }