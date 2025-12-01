import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class UnitMediaInfo(BaseModel):
    """Schema for UnitMedia record."""

    model_config = {
        "populate_by_name": True,
        "alias_generator": None,
    }

    # Field definitions with camelCase aliases for Core API
    id: str
    project_id: str = Field(alias="projectId")
    file_name: str = Field(alias="fileName")
    file_url: str = Field(alias="fileUrl")
    file_link_id: str = Field(alias="fileLinkId")
    s3_url: str | None = Field(default=None, alias="s3Url")
    mime_type: str = Field(alias="mimeType")
    caption: str | None = None
    extracted_features: dict[str, Any] | None = Field(default=None, alias="extractedFeatures")
    caption_embedding: list[float] | None = Field(default=None, alias="captionEmbedding")


class UnitMediaUpdate(BaseModel):
    """Schema for updating UnitMedia record."""

    caption: str | None = None
    s3_url: str | None = None
    extracted_features: dict[str, Any] | None = None
    caption_embedding: list[float] | None = None


class UnitMediaCreate(BaseModel):
    """Schema for creating new UnitMedia record."""
    
    # Core API uses camelCase, so project_id becomes projectId
    project_id: str  # Will be converted to projectId by API
    file_name: str   # Will be converted to fileName
    file_url: str    # Will be converted to fileUrl  
    file_link_id: str # Will be converted to fileLinkId
    s3_url: str | None = None  # Will be converted to s3Url
    mime_type: str   # Will be converted to mimeType
    caption: str | None = None
    extracted_features: dict[str, Any] | None = None
    
    def model_dump(self, **kwargs) -> dict[str, Any]:  # type: ignore[override]
        """Convert to camelCase format for Core API."""
        data = super().model_dump(**kwargs)
        result = {
            "projectId": data["project_id"],
            "fileName": data["file_name"],
            "fileUrl": data["file_url"],
            "fileLinkId": data["file_link_id"],
            "mimeType": data["mime_type"],
        }
        # Добавляем optional поля только если они не None
        if data.get("s3_url") is not None:
            result["s3Url"] = data["s3_url"]
        if data.get("caption") is not None:
            result["caption"] = data["caption"]
        if data.get("extracted_features") is not None:
            result["extractedFeatures"] = data["extracted_features"]
        return result


class UnitMediaClient:
    """Client for working with unit_media records through Core API."""

    def __init__(self, core_client):
        self.client = core_client

    async def create(self, create_data: UnitMediaCreate) -> UnitMediaInfo:
        """Create new unit media record.

        Args:
            create_data: Data to create unit media record

        Returns:
            UnitMediaInfo: Created media information
        """
        logger.debug(f"Creating unit media for project: {create_data.project_id}")
        payload = create_data.model_dump()
        logger.debug(f"POST payload: {payload}")
        try:
            response = await self.client._post("/api/unit-media/", data=payload)
            logger.debug(f"POST response: {response}")
            return UnitMediaInfo.model_validate(response)
        except Exception as e:
            logger.error(f"POST failed with payload: {payload}")
            logger.error(f"Error: {e}")
            # Попробуем извлечь детали ошибки
            error_details = getattr(e, 'response_data', None) or getattr(e, 'body', None)
            if error_details:
                logger.error(f"Error details: {error_details}")
            raise

    async def get(self, media_id: str) -> UnitMediaInfo:
        """Get unit media record by ID.

        Args:
            media_id: UUID of the media record

        Returns:
            UnitMediaInfo: Typed media information
        """
        logger.debug(f"Getting unit media info for media_id: {media_id}")
        response = await self.client._get(f"/api/unit-media/{media_id}/")
        return UnitMediaInfo.model_validate(response)

    async def update(self, media_id: str, update_data: dict[str, Any]) -> UnitMediaInfo:
        """Update unit media record.

        Args:
            media_id: UUID of the media record
            update_data: Data to update

        Returns:
            UnitMediaInfo: Updated media information
        """
        logger.debug(f"Updating unit media {media_id} with data keys: {list(update_data.keys())}")
        response = await self.client._patch(f"/api/unit-media/{media_id}/", data=update_data)
        return UnitMediaInfo.model_validate(response)

    async def update_status(
        self, media_id: str, status: str, error_message: str | None = None
    ) -> None:
        """Update processing status of unit media.

        Args:
            media_id: UUID of the media record
            status: New status (PROCESSING, PROCESSED, FAILED)
            error_message: Optional error message if failed
        """
        update_data = {"status": status}
        if error_message:
            update_data["error_message"] = error_message

        logger.debug(f"Updating status for unit media {media_id} to {status}")
        await self.client._patch(f"/api/unit-media/{media_id}/status/", data=update_data)

    async def update_features(
        self,
        media_id: str,
        extracted_features: dict[str, Any],
        caption: str | None = None,
        caption_embedding: list[float] | None = None,
    ) -> UnitMediaInfo:
        """Update extracted features and related fields.

        Args:
            media_id: UUID of the media record
            extracted_features: JSON features extracted from image
            caption: Optional caption text
            caption_embedding: Optional embedding vector

        Returns:
            UnitMediaInfo: Updated media information
        """
        # Convert to camelCase for API
        update_data = {"extractedFeatures": extracted_features}

        if caption is not None:
            update_data["caption"] = caption

        if caption_embedding is not None:
            update_data["captionEmbedding"] = caption_embedding

        logger.debug(f"Updating features for unit media {media_id}")
        return await self.update(media_id, update_data)
