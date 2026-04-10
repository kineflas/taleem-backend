from pydantic import BaseModel
from datetime import datetime
import uuid
from ..models.notification import NotificationType


class NotificationOut(BaseModel):
    id: uuid.UUID
    recipient_id: uuid.UUID
    type: NotificationType
    title: str
    body: str
    related_task_id: uuid.UUID | None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}
