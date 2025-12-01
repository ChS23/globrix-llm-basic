# agent/tools/genui_tool.py

from typing import Dict, Any
from services.core_api_client.presentations import PresentationsClient
from services.core_api_client.base_client import CoreApiClient

async def genui_tool(property_data: Dict[str, Any]) -> str:
    """
    Генерирует HTML презентацию (лэндинг) для недвижимости.
    """
    client = CoreApiClient(
        base_url="http://core-api:8000",  # Замените на реальный URL
        api_key="your-api-key"            # Если нужен
    )
    presentations_client = PresentationsClient(api_client=client)

    try:
        project_id = property_data.get("project_id")
        if not project_id:
            return "Ошибка: не указан project_id"

        html_content = await presentations_client.render(presentation_id=project_id)
        return html_content

    except Exception as e:
        print(f"Ошибка при генерации презентации: {e}")
        return f"Ошибка: {str(e)}"