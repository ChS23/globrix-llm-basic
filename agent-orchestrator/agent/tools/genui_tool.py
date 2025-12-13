"""GenUI Tool - обёртка для вызова GenUI Agent из главного агента.

Этот tool используется Realtor Agent для обновления UI состояния сделки.
Внутри запускается полноценный GenUI Agent (LangGraph).
"""

import structlog
from typing import Dict, Any
from langchain_core.tools import tool

from agent.genui.agent import GenUIAgent

logger = structlog.get_logger(__name__)

# Global GenUI Agent instance (singleton)
_genui_agent: GenUIAgent | None = None


def get_genui_agent() -> GenUIAgent:
    """Get or create GenUI Agent instance."""
    global _genui_agent
    if _genui_agent is None:
        _genui_agent = GenUIAgent()
        logger.info("Initialized GenUI Agent")
    return _genui_agent


@tool
async def genui_tool(deal_id: str, instruction: str) -> str:
    """Обновление визуального интерфейса страницы сделки.

    Этот инструмент вызывает GenUI Agent для трансформации UI:
    1. Загружает текущее состояние страницы из базы данных
    2. Анализирует инструкцию с помощью LLM
    3. Генерирует обновлённые UI блоки
    4. Валидирует блоки по схемам компонентов
    5. Сохраняет новое состояние

    Args:
        deal_id: UUID сделки (используй deal_id из контекста сообщения)
        instruction: Детальная инструкция что изменить в UI.

                    ВАЖНО для апартаментов:
                    Передавай РЕАЛЬНЫЕ данные из search_apartments в формате:
                    "Добавь карточки апартаментов: [
                      {{"id": "реальный_id", "type": "2br", "area": 85, "price": 1500000, "currency": "AED", "status": "available"}},
                      ...
                    ]"

    Returns:
        Результат операции: успех с описанием изменений или ошибка

    Когда использовать:
        ✓ После search_apartments — чтобы показать найденные апартаменты на странице
        ✓ Клиент просит "покажи", "выведи", "отобрази" результаты
        ✓ Нужно обновить фильтры или другие UI элементы

    Критически важно:
        - Передавай в instruction ТОЛЬКО реальные данные из результатов поиска
        - НЕ выдумывай id, цены, площади или характеристики
        - Используй deal_id из контекста [Context: Current deal_id = ...]
    """
    logger.info(f"GenUI tool called for deal {deal_id}")

    try:
        # Get GenUI Agent
        agent = get_genui_agent()

        # Run agent
        result = await agent.run(deal_id=deal_id, instruction=instruction)

        # Check result
        if not result["success"]:
            error_msg = f"❌ Failed to update UI: {result['error']}"
            logger.error(error_msg)
            return error_msg

        # Success - return summary
        blocks = result["blocks"]
        block_summary = _summarize_blocks(blocks)

        success_msg = f"✅ Updated deal page with {len(blocks)} blocks:\n{block_summary}"

        if result.get("reasoning"):
            success_msg += f"\n\nReasoning: {result['reasoning'][:200]}..."

        logger.info(f"GenUI tool succeeded: {len(blocks)} blocks")
        return success_msg

    except Exception as e:
        error_msg = f"❌ GenUI tool error: {str(e)}"
        logger.error(error_msg)
        return error_msg


def _summarize_blocks(blocks: list[Dict[str, Any]]) -> str:
    """Summarize blocks for user-friendly output."""
    if not blocks:
        return "No blocks"

    summary = []
    for block in blocks:
        block_type = block.get("type", "unknown")
        props = block.get("props", {})

        # For items array, show count
        if "items" in props and isinstance(props["items"], list):
            summary.append(f"- {block_type}: {len(props['items'])} items")
        else:
            summary.append(f"- {block_type}")

    return "\n".join(summary)


