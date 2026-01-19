"""Event models for API responses."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class EventResponse(BaseModel):
    """Response model for a single Kubernetes event."""
    name: str
    namespace: str
    type: str  # Normal, Warning
    reason: str
    message: str
    source_component: Optional[str] = None
    source_host: Optional[str] = None
    involved_object_kind: str
    involved_object_name: str
    involved_object_namespace: Optional[str] = None
    involved_object_uid: Optional[str] = None
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    count: int = 1
    creation_timestamp: datetime
    uid: str


class EventListResponse(BaseModel):
    """Response model for listing events."""
    items: List[EventResponse]
    total: int


def event_to_response(event_dict: Dict[str, Any]) -> EventResponse:
    """Convert Kubernetes event dict to EventResponse."""
    metadata = event_dict.get("metadata", {})
    
    # Handle involved object
    involved_object = event_dict.get("involved_object", {})
    
    # Handle source
    source = event_dict.get("source", {})
    
    # Parse timestamps
    first_timestamp = None
    last_timestamp = None
    creation_timestamp = metadata.get("creation_timestamp")

    # Handle first_timestamp
    if event_dict.get("first_timestamp"):
        ts = event_dict["first_timestamp"]
        if isinstance(ts, str):
            try:
                first_timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        elif hasattr(ts, 'isoformat'):  # datetime object
            first_timestamp = ts

    # Handle last_timestamp
    if event_dict.get("last_timestamp"):
        ts = event_dict["last_timestamp"]
        if isinstance(ts, str):
            try:
                last_timestamp = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
        elif hasattr(ts, 'isoformat'):  # datetime object
            last_timestamp = ts

    # Handle creation_timestamp
    if creation_timestamp:
        if isinstance(creation_timestamp, str):
            try:
                creation_timestamp = datetime.fromisoformat(creation_timestamp.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                creation_timestamp = datetime.now()
        elif hasattr(creation_timestamp, 'isoformat'):  # datetime object
            pass  # already a datetime
    else:
        creation_timestamp = datetime.now()
    
    return EventResponse(
        name=metadata.get("name") or "",
        namespace=metadata.get("namespace") or "",
        type=event_dict.get("type") or "Normal",
        reason=event_dict.get("reason") or "",
        message=event_dict.get("message") or "",
        source_component=source.get("component"),
        source_host=source.get("host"),
        involved_object_kind=involved_object.get("kind") or "",
        involved_object_name=involved_object.get("name") or "",
        involved_object_namespace=involved_object.get("namespace"),
        involved_object_uid=involved_object.get("uid"),
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
        count=event_dict.get("count") or 1,
        creation_timestamp=creation_timestamp,
        uid=metadata.get("uid") or ""
    )
