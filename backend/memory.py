from datetime import datetime
from typing import Dict, List, Optional
import json
import os


class ConversationMemory:
    """사용자별 대화 이력을 관리하는 클래스"""
    
    def __init__(self, max_messages: int = 6):
        """
        Args:
            max_messages: 사용자별 최대 저장할 메시지 수 (기본 6개 = 3번의 질답)
        """
        self.conversations: Dict[str, List[dict]] = {}
        self.max_messages = max_messages
        self.memory_file = "conversation_memory.json"
        self._load_from_file()
    
    def add_message(self, user_id: str, role: str, content: str, regulation_file: Optional[str] = None) -> None:
        """대화 메시지 추가"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # 어시스턴트 응답인 경우 선택된 규정 정보도 저장
        if role == "assistant" and regulation_file:
            message["regulation_file"] = regulation_file
        
        self.conversations[user_id].append(message)
        
        # 최대 메시지 수 제한 (최근 6개만 유지)
        if len(self.conversations[user_id]) > self.max_messages:
            self.conversations[user_id] = self.conversations[user_id][-self.max_messages:]
        
        # 파일에 자동 저장
        self._save_to_file()
    
    def get_conversation_history(self, user_id: str, limit: Optional[int] = None) -> List[dict]:
        """사용자의 대화 이력 조회"""
        if user_id not in self.conversations:
            return []
        
        history = self.conversations[user_id]
        if limit:
            return history[-limit:]
        return history
    
    def build_context_string(self, user_id: str, include_regulation_info: bool = True) -> str:
        """GPT 컨텍스트용 대화 이력 문자열 생성
        
        Args:
            user_id: 사용자 ID
            include_regulation_info: 규정 정보 포함 여부 (기본 True)
                - True: 분류 에이전트용 (규정 정보 포함)
                - False: 응답 에이전트용 (순수 대화 내용만)
        """
        history = self.get_conversation_history(user_id)
        if not history:
            return ""
        
        context_lines = []
        for msg in history:
            if msg["role"] == "user":
                context_lines.append(f"사용자: {msg['content']}")
            else:
                if include_regulation_info:
                    # 분류 에이전트용: 규정 정보 포함
                    regulation_info = ""
                    if "regulation_file" in msg and msg["regulation_file"] != "default.txt":
                        regulation_name = msg["regulation_file"].replace(".txt", "")
                        regulation_info = f" [사용된 규정: {regulation_name}]"
                    context_lines.append(f"어시스턴트: {msg['content']}{regulation_info}")
                else:
                    # 응답 에이전트용: 순수 대화 내용만
                    context_lines.append(f"어시스턴트: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def clear_user_history(self, user_id: str) -> None:
        """특정 사용자의 대화 이력 삭제"""
        if user_id in self.conversations:
            del self.conversations[user_id]
            self._save_to_file()
    
    def clear_all_history(self) -> None:
        """모든 대화 이력 삭제"""
        self.conversations = {}
        self._save_to_file()
    
    def _save_to_file(self) -> None:
        """메모리를 파일에 저장"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save conversation memory: {e}")
    
    def _load_from_file(self) -> None:
        """파일에서 메모리 로드"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.conversations = json.load(f)
                print(f"Loaded conversation memory from {self.memory_file}")
        except Exception as e:
            print(f"Warning: Failed to load conversation memory: {e}")
            self.conversations = {}
    
    def get_stats(self) -> dict:
        """메모리 통계 정보"""
        total_users = len(self.conversations)
        total_messages = sum(len(msgs) for msgs in self.conversations.values())
        
        return {
            "total_users": total_users,
            "total_messages": total_messages,
            "max_messages_per_user": self.max_messages
        }