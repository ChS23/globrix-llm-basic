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
    await logger.ainfo("read_deal_state START", deal_id=deal_id)

    try:
        deal = await deal_crud.get_by_id(deal_id)

        if not deal:
            await logger.awarning(
                "read_deal_state: Deal not found, returning empty state",
                deal_id=deal_id,
            )
            return {
                "deal_id": deal_id,
                "blocks": [],
                "metadata": {"created_at": None},
            }

        ui_state = deal.get("ui_state") or {"blocks": []}
        blocks = ui_state.get("blocks", [])

        await logger.ainfo(
            "read_deal_state DONE",
            deal_id=deal_id,
            blocks_count=len(blocks),
            blocks_types=[b.get("type") for b in blocks],
            ui_state_keys=list(ui_state.keys()) if ui_state else [],
        )

        return {
            "deal_id": deal_id,
            "blocks": blocks,
            "metadata": ui_state.get("metadata", {}),
        }

    except Exception as e:
        await logger.aerror(
            "read_deal_state FAILED",
            deal_id=deal_id,
            error=str(e),
            error_type=type(e).__name__,
        )
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
    await logger.ainfo(
        "write_deal_state START",
        deal_id=deal_id,
        blocks_count=len(blocks),
        blocks_types=[b.get("type") for b in blocks],
    )

    try:
        # Prepare UI state
        ui_state = {
            "deal_id": deal_id,
            "blocks": blocks,
            "metadata": metadata or {},
        }

        await logger.adebug(
            "write_deal_state: prepared ui_state",
            deal_id=deal_id,
            ui_state=ui_state,
        )

        # Check if deal exists
        existing_deal = await deal_crud.get_by_id(deal_id)

        if existing_deal:
            # Update existing deal
            await deal_crud.update(deal_id=deal_id, ui_state=ui_state)
            await logger.ainfo(
                "write_deal_state: UPDATED existing deal",
                deal_id=deal_id,
                blocks_count=len(blocks),
            )
        else:
            # Create new deal
            await deal_crud.create(deal_id=deal_id, ui_state=ui_state)
            await logger.ainfo(
                "write_deal_state: CREATED new deal",
                deal_id=deal_id,
                blocks_count=len(blocks),
            )

        await logger.ainfo("write_deal_state DONE", deal_id=deal_id)
        return True

    except Exception as e:
        await logger.aerror(
            "write_deal_state FAILED",
            deal_id=deal_id,
            error=str(e),
            error_type=type(e).__name__,
        )
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
        await logger.aerror("validate_block FAILED: no type field", block=block)
        raise ValueError("Block must have 'type' field")

    # Fetch schemas
    schemas = await fetch_component_schemas()

    if block_type not in schemas:
        await logger.aerror(
            "validate_block FAILED: unknown block type",
            block_type=block_type,
            available_types=list(schemas.keys()),
        )
        raise ValueError(f"Unknown block type: {block_type}")

    # TODO: Implement JSON Schema validation
    # For now, just check that props exist
    if "props" not in block:
        await logger.aerror(
            "validate_block FAILED: no props field",
            block_type=block_type,
            block=block,
        )
        raise ValueError(f"Block of type '{block_type}' must have 'props' field")

    await logger.adebug(
        "validate_block: OK",
        block_type=block_type,
        props_keys=list(block.get("props", {}).keys()),
    )
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
    await logger.ainfo(
        "validate_blocks START",
        blocks_count=len(blocks),
        blocks_types=[b.get("type") for b in blocks],
    )

    for i, block in enumerate(blocks):
        try:
            await validate_block(block)
        except ValueError as e:
            await logger.aerror(
                "validate_blocks FAILED",
                block_index=i,
                block=block,
                error=str(e),
            )
            raise ValueError(f"Block at index {i} is invalid: {e}")

    await logger.ainfo(
        "validate_blocks DONE",
        blocks_count=len(blocks),
    )
    return True
