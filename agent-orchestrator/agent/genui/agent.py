"""GenUI Agent - LangGraph агент для трансформации UI состояния сделки.

Этот агент работает как инструмент главного агента (Realtor Agent).
Он читает инструкцию, анализирует текущее состояние UI, и создаёт
обновлённое состояние с новыми блоками.
"""

import os
import structlog
from datetime import datetime
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

from .state import GenUIState
from .tools import (
    read_deal_state,
    write_deal_state,
    validate_blocks,
)
from .dependencies import get_deal_crud, get_component_schema_service, ComponentSchemaService
from services.supabase_client.deal_crud import DealCRUD

logger = structlog.get_logger(__name__)

# === Configuration ===

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("GENUI_MODEL", "claude-3-5-sonnet-20241022")


# === GenUI Agent ===


class GenUIAgent:
    """GenUI Agent для трансформации UI состояния сделки.

    Использует LangGraph для reasoning и принятия решений.
    """

    def __init__(
        self,
        deal_crud: DealCRUD | None = None,
        schema_service: ComponentSchemaService | None = None,
    ):
        """Initialize GenUI Agent.

        Args:
            deal_crud: DealCRUD instance (dependency injection)
                      If None, will be created via get_deal_crud()
            schema_service: ComponentSchemaService instance (dependency injection)
                           If None, will be created via get_component_schema_service()
        """
        self.llm = ChatAnthropic(
            api_key=ANTHROPIC_API_KEY,
            model=MODEL_NAME,
            temperature=0,  # Детерминистичность для UI генерации
        )
        self.deal_crud = deal_crud or get_deal_crud()
        self.schema_service = schema_service or get_component_schema_service()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build LangGraph for GenUI Agent."""
        workflow = StateGraph(GenUIState)

        # Nodes
        workflow.add_node("load_context", self._load_context)
        workflow.add_node("analyze_instruction", self._analyze_instruction)
        workflow.add_node("transform_ui", self._transform_ui)
        workflow.add_node("save_state", self._save_state)

        # Edges
        workflow.set_entry_point("load_context")
        workflow.add_edge("load_context", "analyze_instruction")
        workflow.add_edge("analyze_instruction", "transform_ui")
        workflow.add_edge("transform_ui", "save_state")
        workflow.add_edge("save_state", END)

        return workflow.compile()

    async def _load_context(self, state: GenUIState) -> GenUIState:
        """Load current UI state and component schemas."""
        logger.info(f"Loading context for deal {state['deal_id']}")

        try:
            # Read current UI state from Supabase
            ui_state = await read_deal_state(state["deal_id"], self.deal_crud)
            state["current_blocks"] = ui_state.get("blocks", [])
            state["metadata"] = ui_state.get("metadata", {})

            # Fetch component schemas from frontend
            schemas = await self.schema_service.get_schemas()
            state["component_schemas"] = schemas

            logger.info(
                f"Loaded {len(state['current_blocks'])} blocks and {len(schemas)} component schemas"
            )

            return state

        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            state["error"] = str(e)
            return state

    async def _analyze_instruction(self, state: GenUIState) -> GenUIState:
        """Analyze instruction from Realtor Agent using LLM."""
        if state.get("error"):
            return state

        logger.info("Analyzing instruction with LLM")

        try:
            # Prepare context for LLM
            current_blocks_summary = self._summarize_blocks(state["current_blocks"])
            available_components = list(state["component_schemas"].keys())

            prompt = f"""You are GenUI Agent. Your job is to transform UI state for a real estate deal page.

**Current UI blocks:**
{current_blocks_summary}

**Available components:**
{', '.join(available_components)}

**Instruction from Realtor Agent:**
{state['instruction']}

**Your task:**
Analyze the instruction and decide what UI changes are needed.
Provide a brief reasoning about what blocks to add, modify, or remove.

Respond in this format:
REASONING: <your analysis>
ACTIONS: <list of actions like "add apartment_cards block with 5 items", "update filters block", etc.>
"""

            response = await self.llm.ainvoke(prompt)
            state["reasoning"] = response.content

            logger.info(f"LLM reasoning: {response.content[:200]}...")

            return state

        except Exception as e:
            logger.error(f"Failed to analyze instruction: {e}")
            state["error"] = str(e)
            return state

    async def _transform_ui(self, state: GenUIState) -> GenUIState:
        """Transform UI blocks based on reasoning."""
        if state.get("error"):
            return state

        logger.info("Transforming UI blocks")

        try:
            # Parse instruction and create new blocks
            # For MVP, we'll use a simple prompt to LLM to generate JSON blocks

            current_blocks_json = state["current_blocks"]
            schemas_json = {
                k: v.get("props_schema")
                for k, v in state["component_schemas"].items()
            }

            prompt = f"""You are GenUI Agent. Generate updated UI blocks for a real estate deal page.

**Current blocks (JSON):**
```json
{current_blocks_json}
```

**Component schemas:**
```json
{schemas_json}
```

**Instruction:**
{state['instruction']}

**Your reasoning:**
{state.get('reasoning', '')}

**Generate updated blocks:**
Return ONLY a valid JSON array of blocks. Each block must have:
- "type": one of the available component types
- "props": matching the component schema

Example:
[
  {{
    "type": "filters",
    "props": {{ "location": "Dubai Marina", "bedrooms": "2br" }}
  }},
  {{
    "type": "apartment_cards",
    "props": {{
      "items": [
        {{ "id": "apt-1", "type": "2br", "area": 120, "price": 1500000, "status": "available", "project_id": "proj-1" }}
      ]
    }}
  }}
]

Return ONLY the JSON array, no other text.
"""

            response = await self.llm.ainvoke(prompt)

            # Parse JSON response
            import json
            content = response.content

            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            new_blocks = json.loads(content)

            # Validate blocks
            await validate_blocks(new_blocks)

            state["new_blocks"] = new_blocks

            logger.info(f"Generated {len(new_blocks)} new blocks")

            return state

        except Exception as e:
            logger.error(f"Failed to transform UI: {e}")
            state["error"] = str(e)
            return state

    async def _save_state(self, state: GenUIState) -> GenUIState:
        """Save updated UI state to Supabase."""
        if state.get("error"):
            logger.error(f"Skipping save due to error: {state['error']}")
            return state

        logger.info("Saving updated UI state")

        try:
            # Update metadata
            metadata = state.get("metadata", {})
            metadata["last_updated"] = datetime.utcnow().isoformat()
            metadata["schema_version"] = "1.0"

            # Write to Supabase
            await write_deal_state(
                deal_id=state["deal_id"],
                blocks=state["new_blocks"],
                deal_crud=self.deal_crud,
                metadata=metadata,
            )

            logger.info(f"Successfully saved UI state for deal {state['deal_id']}")

            return state

        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            state["error"] = str(e)
            return state

    def _summarize_blocks(self, blocks: list[Dict[str, Any]]) -> str:
        """Summarize current blocks for LLM context."""
        if not blocks:
            return "No blocks (empty page)"

        summary = []
        for i, block in enumerate(blocks):
            block_type = block.get("type", "unknown")
            props_summary = self._summarize_props(block.get("props", {}))
            summary.append(f"{i+1}. {block_type}: {props_summary}")

        return "\n".join(summary)

    def _summarize_props(self, props: Dict[str, Any]) -> str:
        """Summarize block props for readability."""
        if not props:
            return "empty props"

        # For items array, show count
        if "items" in props and isinstance(props["items"], list):
            return f"{len(props['items'])} items"

        # For other props, show key names
        return f"keys: {', '.join(props.keys())}"

    async def run(
        self, deal_id: str, instruction: str
    ) -> Dict[str, Any]:
        """Run GenUI Agent to transform UI state.

        Args:
            deal_id: UUID сделки
            instruction: Инструкция от Realtor Agent

        Returns:
            Dict with result:
            {
                "success": bool,
                "blocks": [...],
                "error": str | None
            }
        """
        logger.info(f"Running GenUI Agent for deal {deal_id}")

        initial_state: GenUIState = {
            "messages": [],
            "deal_id": deal_id,
            "instruction": instruction,
            "current_blocks": [],
            "new_blocks": [],
            "component_schemas": None,
            "metadata": None,
            "reasoning": None,
            "error": None,
        }

        try:
            final_state = await self.graph.ainvoke(initial_state)

            if final_state.get("error"):
                return {
                    "success": False,
                    "blocks": [],
                    "error": final_state["error"],
                }

            return {
                "success": True,
                "blocks": final_state["new_blocks"],
                "reasoning": final_state.get("reasoning"),
                "error": None,
            }

        except Exception as e:
            logger.error(f"GenUI Agent failed: {e}")
            return {"success": False, "blocks": [], "error": str(e)}
