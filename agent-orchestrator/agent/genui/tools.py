"""Internal tools for GenUI Agent.

Эти инструменты используются внутри GenUI Agent для:
- Чтения текущего состояния UI сделки из Supabase
- Записи обновлённого состояния UI в Supabase
- Валидации блоков против схем компонентов
"""

import os
import structlog
from typing import Dict, Any, Optional
import httpx

from services.supabase_client.base_client import SupabaseClientService
from services.supabase_client.deal_crud import DealCRUD

logger = structlog.get_logger(__name__)

# === Configuration ===

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


# === Supabase Client Initialization ===

_supabase_service: Optional[SupabaseClientService] = None
_deal_crud: Optional[DealCRUD] = None


def get_deal_crud() -> DealCRUD:
    """Get or initialize DealCRUD instance."""
    global _supabase_service, _deal_crud

    if _deal_crud is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        _supabase_service = SupabaseClientService.get_instance(
            url=SUPABASE_URL, key=SUPABASE_KEY
        )
        _deal_crud = DealCRUD(_supabase_service)

    return _deal_crud


# === Component Schemas Cache ===

_component_schemas_cache: Optional[Dict[str, Any]] = None


async def fetch_component_schemas() -> Dict[str, Any]:
    """Fetch UI component schemas from frontend API.

    Кэширует схемы для последующих вызовов.

    Returns:
        Dict со схемами всех компонентов

    Raises:
        Exception: При ошибке запроса к API
    """
    global _component_schemas_cache

    if _component_schemas_cache is not None:
        return _component_schemas_cache

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FRONTEND_URL}/api/ui-components")
            response.raise_for_status()
            data = response.json()

            _component_schemas_cache = data.get("schemas", {})
            logger.info(
                f"Fetched {len(_component_schemas_cache)} component schemas from frontend"
            )

            return _component_schemas_cache

    except Exception as e:
        logger.error(f"Failed to fetch component schemas: {e}")
        raise


# === Deal State Tools ===


async def read_deal_state(deal_id: str) -> Dict[str, Any]:
    """Read current UI state for a deal from Supabase.

    Args:
        deal_id: UUID сделки

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
        deal_crud = get_deal_crud()
        deal = await deal_crud.get_by_id(deal_id)

        if not deal:
            logger.warning(f"Deal {deal_id} not found, returning empty state")
            return {
                "deal_id": deal_id,
                "blocks": [],
                "metadata": {"created_at": None},
            }

        ui_state = deal.get("ui_state") or {"blocks": []}

        logger.info(f"Read deal state for {deal_id}: {len(ui_state.get('blocks', []))} blocks")

        return {
            "deal_id": deal_id,
            "blocks": ui_state.get("blocks", []),
            "metadata": ui_state.get("metadata", {}),
        }

    except Exception as e:
        logger.error(f"Failed to read deal state for {deal_id}: {e}")
        raise


async def write_deal_state(
    deal_id: str, blocks: list[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Write updated UI state to Supabase.

    Args:
        deal_id: UUID сделки
        blocks: Массив UI блоков
        metadata: Метаданные (опционально)

    Returns:
        True если успешно сохранено

    Raises:
        Exception: При ошибке записи в Supabase
    """
    try:
        deal_crud = get_deal_crud()

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
            logger.info(f"Updated deal state for {deal_id}: {len(blocks)} blocks")
        else:
            # Create new deal
            await deal_crud.create(deal_id=deal_id, ui_state=ui_state)
            logger.info(f"Created new deal {deal_id} with {len(blocks)} blocks")

        return True

    except Exception as e:
        logger.error(f"Failed to write deal state for {deal_id}: {e}")
        raise


# === Validation Tools ===


async def validate_block(block: Dict[str, Any]) -> bool:
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

    logger.debug(f"Block type '{block_type}' validated successfully")
    return True


async def validate_blocks(blocks: list[Dict[str, Any]]) -> bool:
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

    logger.info(f"Validated {len(blocks)} blocks successfully")
    return True
