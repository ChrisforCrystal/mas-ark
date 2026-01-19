"""Health check response models."""
from typing import Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status", example="healthy")
    service: str = Field(..., description="Service name", example="ark-api")


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    status: str = Field(..., description="Readiness status", example="ready")
    service: str = Field(..., description="Service name", example="ark-api")
    error: Optional[str] = Field(None, description="Error message if not ready", example="Connection refused")
