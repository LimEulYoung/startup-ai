import os
import asyncio
from typing import Dict, List
from agents import Agent, Runner, trace, ModelSettings



class RegulationAgentSystem:
    def __init__(self):
        self.regulations = self._load_regulations()
        self.specialist_agents = self._create_specialist_agents()
        self.orchestrator_agent = self._create_orchestrator_agent()
    
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
    
    def _create_specialist_agents(self) -> Dict[str, Agent]:
        """각 규정별 전문 에이전트 생성"""
        agents = {}
        
        # 규정별 에이전트 정의
        regulation_configs = {
            "중소기업창업 지원사업 운영요령(중소벤처기업부고시)(제2024-101호)(20241206).txt": {
                "name": "startup_support_agent",
                "description": "창업지원사업 운영, 신청자격, 절차, 협약, 관리감독 전문가"
            },
            "창업사업화 지원사업 통합관리지침.txt": {
                "name": "budget_management_agent", 
                "description": "예산집행, 수당지급, 회계처리, 사업비 관리 전문가"
            },
            "전문계약직 운영지침.txt": {
                "name": "contract_employee_agent",
                "description": "전문계약직 채용, 급여, 연봉, 근무조건 전문가"
            },
            "위임전결규정.txt": {
                "name": "delegation_agent",
                "description": "업무처리 권한, 결재절차, 위임전결사항 전문가"
            },
            "국외출장 등에 대한 관리지침.txt": {
                "name": "overseas_trip_agent",
                "description": "국외출장 절차, 출장비, 허가기준, 심사방법 전문가"
            },
            "여비규정.txt": {
                "name": "travel_expense_agent",
                "description": "출장여비, 일비, 숙박비, 여행경비 기준 전문가"
            },
            "보수규정.txt": {
                "name": "salary_agent",
                "description": "연봉, 급여체계, 각종 수당 금액 전문가"
            },
            "복무규정.txt": {
                "name": "work_regulation_agent",
                "description": "근무시간, 휴가일수, 근무규칙, 출결관리 전문가"
            },
            "직위운용규칙.txt": {
                "name": "position_agent",
                "description": "직위 호칭, 직급 체계, 직책 호칭 전문가"
            },
            "직제규정.txt": {
                "name": "organization_agent", 
                "description": "조직구조, 부서별 업무, 직급체계, 정원 전문가"
            },
            "채용 지침.txt": {
                "name": "recruitment_agent",
                "description": "채용절차, 심사기준, 면접전형, 합격자 결정 전문가"
            },
            "청년인턴 운영지침.txt": {
                "name": "youth_intern_agent",
                "description": "청년인턴 채용, 급여, 근무조건, 평가, 멘토링 전문가"
            },
            "취업규칙.txt": {
                "name": "employment_rule_agent",
                "description": "근로조건, 취업규칙, 근무시간, 휴가, 급여, 복무 전문가"
            },
            "퇴직금 지급 규정.txt": {
                "name": "retirement_pay_agent",
                "description": "퇴직금, 퇴직급여 계산, 지급조건, 명예퇴직수당 전문가"
            }
        }
        
        # 직급 정보 추가
        job_grade_info = """
직급 정보:
- 3급: 차장
- 4급: 과장  
- 5급: 주임 또는 대리
- 6급: 사원
- 팀장: 1(나)급, 1(가)급, 또는 2급 직원 중 하나
"""
        
        for filename, config in regulation_configs.items():
            if filename in self.regulations:
                regulation_content = self.regulations[filename]
                
                instructions = f"""당신은 창업진흥원 {config['description']}입니다.
주어진 규정을 바탕으로 사용자 질문에 정확하고 간결한 답변을 제공하세요.

답변 규칙:
1. 반드시 한 줄로 연속된 텍스트로만 답변 (줄바꿈, 리스트, 구분자 금지)
2. 카카오톡 메신저에서 사용할 것이므로 줄바꿈 없는 일반 텍스트만 사용
3. 불렛포인트(-), 번호매기기(1.), 줄바꿈(\\n) 절대 금지
4. 질문에 정확히 대응하는 내용만 답변
5. 수당/금액 질문이면 구체적 수치와 간단한 설명을 한 문장으로
6. 카카오톡 대화하듯 친근하고 자연스럽게
7. 모든 정보를 쉼표나 접속사로 연결하여 하나의 연속된 문장으로 구성

{job_grade_info}

관련 규정:
{regulation_content[:45000]}"""

                agent = Agent(
                    name=config["name"],
                    instructions=instructions,
                    handoff_description=config["description"],
                    model="gpt-4o"
                    #model_settings=ModelSettings(
                    #    reasoning={"effort": "medium"}
                    #)
                )
                
                agents[filename] = agent
        
        return agents
    
    def _create_orchestrator_agent(self) -> Agent:
        """모든 전문 에이전트를 도구로 활용하는 오케스트레이터 에이전트 생성"""
        
        # 전문 에이전트들을 도구로 변환
        tools = []
        for filename, agent in self.specialist_agents.items():
            tools.append(
                agent.as_tool(
                    tool_name=f"consult_{agent.name}",
                    tool_description=agent.handoff_description
                )
            )
        
        orchestrator_instructions = """당신은 창업진흥원 규정 질의응답 전문 오케스트레이터입니다.
사용자의 질문을 분석하여 가장 적합한 전문가에게 자문을 요청하세요.

**절대적 규칙:**
1. 절대로 자신이 직접 답변하지 마세요
2. 반드시 제공된 도구(전문가)를 호출하세요
3. 전문가의 답변을 받으면 한 글자도 수정하거나 추가하지 말고 그대로 전달하세요
4. 전문가 답변에 설명이나 추가 정보를 덧붙이지 마세요
5. 전문가 답변을 재구성하거나 정리하지 마세요
6. 전문가가 답변한 그 내용을 변경 없이 그대로 사용자에게 전달하는 것이 유일한 역할입니다

질문의 핵심 의도를 파악해서 다음 규정 전문가 중 가장 적합한 전문가를 선택하세요:

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

한 번에 하나의 전문가만 호출하세요.
전문가의 답변을 받으면 어떤 수정이나 추가도 하지 말고 전문가의 원본 답변을 그대로 반환하세요."""
        
        return Agent(
            name="regulation_orchestrator",
            instructions=orchestrator_instructions,
            tools=tools,
            model="gpt-4o"
            #model_settings=ModelSettings(
            #    reasoning={"effort": "medium"}
            #)
        )
    
    async def search(self, user_query: str) -> dict:
        """사용자 질의에 대한 답변 생성"""
        try:
            with trace("Regulation Q&A"):
                result = await Runner.run(
                    starting_agent=self.orchestrator_agent,
                    input=user_query
                )
                
                # 사용된 에이전트 추적
                used_agents = []
                agent_descriptions = []
                
                # result 객체에서 function call 정보 추출
                if hasattr(result, 'new_items'):
                    for item in result.new_items:
                        if hasattr(item, 'raw_item') and hasattr(item.raw_item, 'name'):
                            tool_name = item.raw_item.name
                            if isinstance(tool_name, str) and tool_name.startswith('consult_'):
                                agent_name = tool_name.replace('consult_', '')
                                used_agents.append(agent_name)
                                
                                # 에이전트명으로 설명 찾기
                                for filename, agent in self.specialist_agents.items():
                                    if agent.name == agent_name:
                                        agent_descriptions.append(agent.handoff_description)
                                        break
                
                # 에이전트 정보가 없으면 기본값 설정
                if not used_agents:
                    used_agents = ["자동_라우팅"]
                    agent_descriptions = ["OpenAI Agents SDK 자동 라우팅"]
                
                return {
                    "query": user_query,
                    "selected_regulations": agent_descriptions,
                    "selected_agents": used_agents,
                    "classification_reason": "에이전트 기반 자동 분류",
                    "answer": result.final_output,
                    "sources": agent_descriptions,
                    "reasoning": "OpenAI Agents SDK 기반 생성",
                    "relevant_sections": []
                }
                
        except Exception as e:
            return {
                "query": user_query,
                "selected_regulations": [],
                "classification_reason": "오류 발생",
                "answer": f"답변 생성 중 오류가 발생했습니다: {str(e)}",
                "sources": [],
                "reasoning": str(e),
                "relevant_sections": []
            }
    
    # 기존 API 호환성을 위한 동기 래퍼
    def search_sync(self, user_query: str) -> dict:
        """동기 버전의 search 메서드"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.search(user_query))