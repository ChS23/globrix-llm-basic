# Определение состояния диалога/сессии
from typing import TypedDict, List
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: List[BaseMessage]
    current_step: str
    last_tool_result: str