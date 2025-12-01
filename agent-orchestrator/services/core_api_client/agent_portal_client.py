"""Agent Portal API client for Telegram Bot MVP."""

import os
from typing import Any, Optional
from uuid import UUID

from .base_client import CoreApiClient


class AgentPortalClient:
    """Client for Agent Portal endpoints in Core API."""

    def __init__(self, client: CoreApiClient):
        self.client = client

    # Bot endpoints
    async def register_agent(
        self,
        telegram_id: str,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
        phone_number: str | None = None,
        email: str | None = None,
        photo_url: str | None = None,
        photo_telegram_file_id: str | None = None,
        telegram_link: str | None = None,
        whatsapp_link: str | None = None,
        custom_link: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        """Register new agent from Telegram bot data."""
        # Use camelCase field names as per updated API schema
        data = {
            "telegramId": telegram_id,
            "firstName": first_name,
            "lastName": last_name,
            "username": username,
            "phoneNumber": phone_number,
            "email": email,
            "photoUrl": photo_url,
            "photoTelegramFileId": photo_telegram_file_id,
            "telegramLink": telegram_link,
            "whatsappLink": whatsapp_link,
            "customLink": custom_link,
            "language": language,
        }
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        return await self.client._post("/api/agent-portal/bot/register", json=data)

    async def search_projects(self, query: str) -> dict[str, Any]:
        """Search projects by name for bot."""
        return await self.client._get(
            "/api/agent-portal/bot/search-projects", params={"query": query}
        )

    # NOTE: generate_materials endpoint removed as it's not implemented in Core API

    # CRUD endpoints
    async def get_agent(self, agent_id: UUID) -> dict[str, Any]:
        """Get agent by ID."""
        return await self.client._get(f"/api/agents/{agent_id}")

    async def get_agents(self, limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """Get list of agents."""
        return await self.client._get("/api/agents", params={"limit": limit, "offset": offset})

    async def find_agent_by_telegram_id(self, telegram_id: str) -> dict[str, Any] | None:
        """Find agent by Telegram ID."""
        try:
            # Используем специальный bot endpoint
            agent = await self.client._get(f"/api/agent-portal/bot/find-agent/{telegram_id}")
            return agent
        except Exception as e:
            # Если агент не найден (404), возвращаем None
            print(f"Agent not found for telegram_id {telegram_id}: {e}")
            return None

    async def get_project_slug(self, project_id: UUID) -> str | None:
        """Get project slug by project ID."""
        try:
            project = await self.client._get(f"/api/projects/{project_id}")
            return project.get("slug")
        except Exception:
            return None

    async def update_agent(self, agent_id: UUID, data: dict[str, Any]) -> dict[str, Any]:
        """Update agent data."""
        return await self.client._patch(f"/api/agents/{agent_id}", json=data)

    async def delete_agent(self, agent_id: UUID) -> None:
        """Delete agent."""
        await self.client._delete(f"/api/agents/{agent_id}")

    # Portal pages
    def get_agent_portal_url(self, agent_id: UUID) -> str:
        """Get agent portal page URL."""
        return f"{self.client.base_url}/agent-portal/{agent_id}"

    def get_prices_download_url(self, agent_id: UUID, project_id: UUID) -> str:
        """Get prices PDF download URL."""
        return f"{self.client.base_url}/api/agents/{agent_id}/projects/{project_id}/prices.pdf"

    def get_presentation_download_url(self, agent_id: UUID, project_id: UUID) -> str:
        """Get presentation PDF download URL."""
        return (
            f"{self.client.base_url}/api/agents/{agent_id}/projects/{project_id}/presentation.pdf"
        )

    def get_prices_web_url(self, agent_slug: str, project_slug: str) -> str:
        """Get prices public web URL with slugs."""
        frontend_base_url = os.getenv("PRESENTATION_FRONTEND_BASE_URL", "https://globrix.pro")
        return f"{frontend_base_url}/agents/{agent_slug}/projects/{project_slug}/pricelist"

    def get_presentation_web_url(self, agent_slug: str, project_slug: str) -> str:
        """Get presentation public web URL with slugs."""
        frontend_base_url = os.getenv("PRESENTATION_FRONTEND_BASE_URL", "https://globrix.pro")
        return f"{frontend_base_url}/agents/{agent_slug}/projects/{project_slug}/presentation"

    def get_compare_projects_web_url(self, agent_slug: str, project_slugs: list[str]) -> str:
        """Get projects comparison public web URL with slugs.

        Args:
            agent_slug: Agent slug
            project_slugs: List of project slugs to compare

        Returns:
            URL like https://globrix.pro/agents/{agent_slug}/compare?projects=slug1,slug2
        """
        frontend_base_url = os.getenv("PRESENTATION_FRONTEND_BASE_URL", "https://globrix.pro")
        projects_param = ",".join(project_slugs)
        return f"{frontend_base_url}/agents/{agent_slug}/compare?projects={projects_param}"
