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
    """Transform UI state for a deal page based on instruction.

    This tool invokes GenUI Agent which:
    1. Reads current UI state from Supabase
    2. Analyzes the instruction using LLM
    3. Generates new UI blocks
    4. Validates blocks against component schemas
    5. Saves updated state to Supabase

    Args:
        deal_id: UUID сделки
        instruction: Инструкция что изменить в UI
                    (например: "Добавь карточки найденных апартаментов")

    Returns:
        Результат в виде строки для главного агента

    Examples:
        >>> await genui_tool(
        ...     deal_id="abc-123",
        ...     instruction="Add apartment cards with search results"
        ... )
        "✅ Updated deal page: added apartment_cards block with 5 items"

        >>> await genui_tool(
        ...     deal_id="abc-123",
        ...     instruction="Show filters: location=Dubai Marina, bedrooms=2br"
        ... )
        "✅ Updated deal page: added filters block"
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


