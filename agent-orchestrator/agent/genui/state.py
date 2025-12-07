"""State schema for GenUI Agent.

Определяет структуру состояния GenUI Agent в LangGraph.
"""

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import MessagesState


class GenUIState(MessagesState):
    """State для GenUI Agent.

    Наследует от MessagesState для поддержки сообщений,
    добавляет специфичные для GenUI поля.
    """

    # Deal context
    deal_id: str
    """UUID сделки"""

    instruction: str
    """Инструкция от главного агента (что изменить в UI)"""

    # Current UI state
    current_blocks: List[Dict[str, Any]]
    """Текущие UI блоки из Supabase"""

    # New UI state (результат работы агента)
    new_blocks: List[Dict[str, Any]]
    """Новые UI блоки после трансформации"""

    # Component schemas
    component_schemas: Optional[Dict[str, Any]]
    """Кэшированные схемы компонентов с фронтенда"""

    # Metadata
    metadata: Optional[Dict[str, Any]]
    """Метаданные (timestamp, версия схемы и т.д.)"""

    # Agent reasoning
    reasoning: Optional[str]
    """Промежуточные рассуждения агента"""

    # Errors
    error: Optional[str]
    """Ошибка, если произошла"""
