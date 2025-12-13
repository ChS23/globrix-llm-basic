"""
Orchestrator Agent - главный агент системы Globrix.

Использует LangGraph ReAct pattern с tool calling.
LLM сам решает какие инструменты вызывать на основе запроса пользователя.
"""

import os
from typing import Literal

import structlog
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool

from agent.tools.retriever_tool import retriever_tool
from agent.tools.genui_tool import genui_tool

logger = structlog.get_logger(__name__)

# === Configuration ===

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("ORCHESTRATOR_MODEL", "openai/gpt-4.1-mini")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = """Ты — AI-ассистент риэлтора Globrix. Помогаешь клиентам с недвижимостью в Дубае и Таиланде.

Твои возможности:
1. **Поиск недвижимости** — используй tool `search_apartments` для поиска апартаментов по параметрам
2. **Информация о проектах** — используй tool `retriever_tool` для поиска в базе знаний о проектах, районах, инфраструктуре
3. **Генерация UI** — используй tool `genui_tool` для обновления страницы сделки (добавление карточек, фильтров и т.д.)

Правила:
- Отвечай на русском языке
- Будь вежливым и профессиональным
- Если не знаешь ответ — честно скажи и предложи уточнить запрос
- Используй tools когда нужна актуальная информация из базы данных
- Форматируй ответы для удобного чтения

ВАЖНО про genui_tool:
- Когда в сообщении есть контекст [Context: Current deal_id = ...], используй этот deal_id при вызове genui_tool
- Когда вызываешь genui_tool после search_apartments, передавай в instruction РЕАЛЬНЫЕ данные апартаментов из результатов поиска
- Пример instruction: "Добавь карточки апартаментов: [{id: 'abc', type: '2br', area: 85, price: 1500000, status: 'available', project_id: 'proj-1'}, ...]"
- НЕ выдумывай данные - используй только реальные результаты из search_apartments
"""


# === Tools ===

@tool
async def search_apartments(
    apartment_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_area: float | None = None,
    max_area: float | None = None,
    status: str | None = None,
    limit: int = 10,
) -> str:
    """Search for apartments in the database.

    Use this tool when the user wants to find apartments or properties.

    Args:
        apartment_type: Type of apartment (studio, 1br, 2br, 3br, 4br, penthouse, duplex, loft)
        min_price: Minimum price filter
        max_price: Maximum price filter
        min_area: Minimum area in sqm
        max_area: Maximum area in sqm
        status: Status filter (available, sold, reserved)
        limit: Maximum number of results (default 10)

    Returns:
        Formatted list of found apartments
    """
    from agent.tools.apartments_search import apartments_search, ApartmentSearchFilter

    filters = ApartmentSearchFilter(
        apartment_type=apartment_type,
        min_price=min_price,
        max_price=max_price,
        min_area=min_area,
        max_area=max_area,
        status=status,
        limit=limit,
    )

    results = await apartments_search(filters)

    if not results:
        return "Апартаменты по заданным критериям не найдены."

    # Format results
    formatted = [f"Найдено {len(results)} апартаментов:\n"]
    for i, apt in enumerate(results[:limit], 1):
        apt_type = apt.get("type", "N/A")
        price = apt.get("price", "N/A")
        area = apt.get("area", "N/A")
        status = apt.get("status", "N/A")
        identifier = apt.get("identifier", "N/A")

        formatted.append(
            f"{i}. **{identifier}** — {apt_type}, {area} м², {price} AED, статус: {status}"
        )

    return "\n".join(formatted)


# === Agent Class ===

class OrchestratorAgent:
    """
    Главный агент-оркестратор.

    Использует LangGraph с ReAct pattern:
    - LLM анализирует запрос и решает какие tools вызвать
    - Tools выполняются
    - LLM формирует финальный ответ
    """

    def __init__(self, checkpointer: MemorySaver):
        self.checkpointer = checkpointer

        # LLM с tool calling через OpenRouter
        self.llm = ChatOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            model=MODEL_NAME,
            temperature=0.3,
        )

        # Доступные tools
        self.tools = [
            search_apartments,
            retriever_tool,
            genui_tool,
        ]

        # LLM с привязанными tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Создаём граф
        self.graph = self._build_graph()

        logger.info("OrchestratorAgent initialized", model=MODEL_NAME, tools=len(self.tools))

    def _build_graph(self) -> StateGraph:
        """Построение LangGraph с ReAct pattern."""

        # Tool node для выполнения tools
        tool_node = ToolNode(self.tools)

        # Определяем граф
        workflow = StateGraph(MessagesState)

        # Nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", tool_node)

        # Entry point
        workflow.set_entry_point("agent")

        # Conditional edges: agent -> tools или END
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )

        # После tools всегда возвращаемся к agent
        workflow.add_edge("tools", "agent")

        return workflow.compile(checkpointer=self.checkpointer)

    async def _call_model(self, state: MessagesState) -> dict:
        """Вызов LLM с системным промптом."""
        messages = state["messages"]

        # Добавляем system prompt если его нет
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

        response = await self.llm_with_tools.ainvoke(messages)

        return {"messages": [response]}

    def _should_continue(self, state: MessagesState) -> Literal["continue", "end"]:
        """Решает продолжать ли выполнение tools или завершить."""
        last_message = state["messages"][-1]

        # Если есть tool_calls — продолжаем
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"

        # Иначе завершаем
        return "end"

    async def ainvoke(self, inputs: dict, config: dict) -> dict:
        """Асинхронный вызов агента."""
        return await self.graph.ainvoke(inputs, config)

    def invoke(self, inputs: dict, config: dict) -> dict:
        """Синхронный вызов агента."""
        return self.graph.invoke(inputs, config)
