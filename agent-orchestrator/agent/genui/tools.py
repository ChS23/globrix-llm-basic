"""Internal tools for GenUI Agent.

Эти инструменты используются внутри GenUI Agent для:
- Чтения текущего состояния UI сделки из Supabase
- Записи обновлённого состояния UI в Supabase
- Валидации блоков против схем компонентов
"""

import os
import structlog
from typing import Any

from services.supabase_client.deal_crud import DealCRUD

logger = structlog.get_logger(__name__)

# === Configuration ===

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")


# === Component Schemas Fetching ===


async def fetch_component_schemas(
    schema_service=None,
) -> dict[str, Any]:
    """Fetch UI component schemas (wrapper for backward compatibility).

    Args:
        schema_service: ComponentSchemaService instance (dependency injection)
                       If None, will use get_component_schema_service()

    Returns:
        Dict со схемами всех компонентов
    """
    if schema_service is None:
        from agent.genui.dependencies import get_component_schema_service
        schema_service = get_component_schema_service()

    return await schema_service.get_schemas()


# === Deal State Tools ===


async def read_deal_state(deal_id: str, deal_crud: DealCRUD) -> dict[str, Any]:
    """Read current UI state for a deal from Supabase.

    Args:
        deal_id: UUID сделки
        deal_crud: DealCRUD instance (dependency injection)

    Returns:
        Dict with deal UI state:
        {
            "deal_id": "abc-123",
            "blocks": [...],
            "metadata": {...}
        }

    Raises:
        Exception: При ошибке чтения из Supabase
    """
    try:
        deal = await deal_crud.get_by_id(deal_id)

        if not deal:
            logger.awarning(f"Deal {deal_id} not found, returning empty state")
            return {
                "deal_id": deal_id,
                "blocks": [],
                "metadata": {"created_at": None},
            }

        ui_state = deal.get("ui_state") or {"blocks": []}

        logger.ainfo(f"Read deal state for {deal_id}: {len(ui_state.get('blocks', []))} blocks")

        return {
            "deal_id": deal_id,
            "blocks": ui_state.get("blocks", []),
            "metadata": ui_state.get("metadata", {}),
        }

    except Exception as e:
        logger.aerror(f"Failed to read deal state for {deal_id}: {e}")
        raise


async def write_deal_state(
    deal_id: str,
    blocks: list[dict[str, Any]],
    deal_crud: DealCRUD,
    metadata: dict[str, Any] | None = None
) -> bool:
    """Write updated UI state to Supabase.

    Args:
        deal_id: UUID сделки
        blocks: Массив UI блоков
        deal_crud: DealCRUD instance (dependency injection)
        metadata: Метаданные (опционально)

    Returns:
        True если успешно сохранено

    Raises:
        Exception: При ошибке записи в Supabase
    """
    try:
        # Prepare UI state
        ui_state = {
            "deal_id": deal_id,
            "blocks": blocks,
            "metadata": metadata or {},
        }

        # Check if deal exists
        existing_deal = await deal_crud.get_by_id(deal_id)

        if existing_deal:
            # Update existing deal
            await deal_crud.update(deal_id=deal_id, ui_state=ui_state)
            logger.ainfo(f"Updated deal state for {deal_id}: {len(blocks)} blocks")
        else:
            # Create new deal
            await deal_crud.create(deal_id=deal_id, ui_state=ui_state)
            logger.ainfo(f"Created new deal {deal_id} with {len(blocks)} blocks")

        return True

    except Exception as e:
        logger.aerror(f"Failed to write deal state for {deal_id}: {e}")
        raise


# === Validation Tools ===


async def validate_block(block: dict[str, Any]) -> bool:
    """Validate a UI block against component schema.

    Args:
        block: UI блок с полями type и props

    Returns:
        True если блок валиден

    Raises:
        ValueError: Если блок не соответствует схеме
    """
    block_type = block.get("type")

    if not block_type:
        raise ValueError("Block must have 'type' field")

    # Fetch schemas
    schemas = await fetch_component_schemas()

    if block_type not in schemas:
        raise ValueError(f"Unknown block type: {block_type}")

    # TODO: Implement JSON Schema validation
    # For now, just check that props exist
    if "props" not in block:
        raise ValueError(f"Block of type '{block_type}' must have 'props' field")

    logger.adebug(f"Block type '{block_type}' validated successfully")
    return True


async def validate_blocks(blocks: list[dict[str, Any]]) -> bool:
    """Validate multiple blocks.

    Args:
        blocks: Массив блоков

    Returns:
        True если все блоки валидны

    Raises:
        ValueError: Если хотя бы один блок невалиден
    """
    for i, block in enumerate(blocks):
        try:
            await validate_block(block)
        except ValueError as e:
            raise ValueError(f"Block at index {i} is invalid: {e}")

    logger.ainfo(f"Validated {len(blocks)} blocks successfully")
    return True
