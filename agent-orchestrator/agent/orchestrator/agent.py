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

import httpx

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("ORCHESTRATOR_MODEL", "openai/gpt-4.1-mini")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def get_http_client():
    """Get httpx client with proxy if configured."""
    proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY") or os.getenv("ALL_PROXY")
    if proxy:
        return httpx.Client(proxy=proxy)
    return None

SYSTEM_PROMPT = """# Роль
Ты — Globrix AI, профессиональный ассистент по недвижимости премиум-класса в Дубае и Таиланде.
Твоя задача — помогать клиентам найти идеальную недвижимость, отвечать на вопросы и управлять сделками.

# Стиль общения
- Язык: всегда отвечай на русском
- Тон: профессиональный, дружелюбный, компетентный
- Формат: структурируй ответы для удобного чтения (списки, выделение ключевой информации)
- Краткость: будь лаконичным, избегай воды

# Доступные инструменты

## 1. search_apartments
Поиск апартаментов в базе данных по параметрам.
КОГДА ИСПОЛЬЗОВАТЬ:
- Клиент хочет найти недвижимость ("найди квартиру", "покажи апартаменты", "что есть в...")
- Клиент указывает параметры: тип, цена, площадь, район
- Нужно подобрать варианты под бюджет или требования

## 2. retriever_tool
Поиск информации в базе знаний: проекты, застройщики, районы, инфраструктура, налоги, правила покупки.
КОГДА ИСПОЛЬЗОВАТЬ:
- Вопросы о конкретных проектах или застройщиках
- Вопросы о районах, инфраструктуре, локациях
- Вопросы о налогах, визах, правилах покупки для иностранцев
- Вопросы о рынке недвижимости в целом

## 3. genui_tool
Обновление визуального интерфейса страницы сделки (добавление карточек апартаментов, фильтров и т.д.)
КОГДА ИСПОЛЬЗОВАТЬ:
- После успешного поиска апартаментов — чтобы показать результаты на странице
- Клиент просит "показать" или "вывести" найденные варианты

# Критически важные правила для genui_tool

1. **deal_id**: Если в сообщении есть `[Context: Current deal_id = UUID]`, ОБЯЗАТЕЛЬНО используй этот UUID как deal_id

2. **Реальные данные**: При вызове genui_tool после search_apartments:
   - Передавай в instruction ТОЛЬКО реальные данные из результатов поиска
   - НИКОГДА не выдумывай id, цены, площади или другие характеристики
   - Копируй данные апартаментов как есть

3. **Формат instruction для апартаментов**:
   ```
   Добавь карточки апартаментов: [
     {"id": "реальный_id_1", "type": "2br", "area": 85, "price": 1500000, "currency": "THB", "status": "available"},
     {"id": "реальный_id_2", "type": "studio", "area": 45, "price": 750000, "currency": "AED", "status": "available"}
   ]
   ```
   ВАЖНО: Всегда указывай РЕАЛЬНУЮ валюту из результатов поиска (AED для Дубая, THB для Таиланда)

# Алгоритм ответа

1. ПОНИМАНИЕ: Определи, что хочет клиент
2. ИНСТРУМЕНТ: Выбери подходящий tool (или несколько)
3. АНАЛИЗ: Обработай результаты
4. ОТВЕТ: Дай структурированный ответ с ключевой информацией
5. UI (опционально): Если есть результаты поиска — обнови интерфейс через genui_tool

# Примеры

Запрос: "Найди двушки до 2 млн"
→ search_apartments(apartment_type="2br", max_price=2000000)
→ genui_tool с реальными результатами
→ Краткий ответ с обзором найденных вариантов

Запрос: "Расскажи про район Dubai Marina"
→ retriever_tool(query="Dubai Marina район инфраструктура")
→ Структурированный ответ о районе

Запрос: "Какие налоги при покупке в Таиланде?"
→ retriever_tool(query="налоги покупка недвижимости Таиланд иностранцы")
→ Ответ с информацией о налогах
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
    """Поиск апартаментов в базе данных по заданным параметрам.

    Используй этот инструмент когда клиент:
    - Хочет найти недвижимость по параметрам
    - Указывает бюджет, тип квартиры, площадь
    - Просит подобрать варианты

    Args:
        apartment_type: Тип апартаментов. Допустимые значения:
            - "studio" — студия
            - "1br" — 1 спальня
            - "2br" — 2 спальни (двушка)
            - "3br" — 3 спальни
            - "4br" — 4+ спальни
            - "penthouse" — пентхаус
            - "duplex" — дуплекс
            - "loft" — лофт
        min_price: Минимальная цена (в валюте региона: AED для Дубая, THB для Таиланда)
        max_price: Максимальная цена
        min_area: Минимальная площадь в м²
        max_area: Максимальная площадь в м²
        status: Статус апартаментов:
            - "available" — доступно для покупки (по умолчанию)
            - "reserved" — забронировано
            - "sold" — продано
        limit: Максимальное количество результатов (по умолчанию 10, максимум 50)

    Returns:
        Форматированный список найденных апартаментов с характеристиками.

    Примеры использования:
        - Найди двушки до 2 млн → apartment_type="2br", max_price=2000000
        - Покажи пентхаусы от 100 м² → apartment_type="penthouse", min_area=100
        - Что есть в продаже до 1 млн? → max_price=1000000, status="available"
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
        currency = apt.get("currency", "AED")  # Get actual currency from API
        area = apt.get("area", "N/A")
        status = apt.get("status", "N/A")
        identifier = apt.get("identifier", "N/A")

        formatted.append(
            f"{i}. **{identifier}** — {apt_type}, {area} м², {price} {currency}, статус: {status}"
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

        # LLM с tool calling через OpenRouter (с прокси если настроен)
        self.llm = ChatOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            model=MODEL_NAME,
            temperature=0.3,
            http_client=get_http_client(),
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
