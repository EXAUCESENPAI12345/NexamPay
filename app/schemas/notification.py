from pydantic import BaseModel


class NotificationItem(BaseModel):
    id: int
    type: str
    title: str
    message: str
    reference_id: str | None
    is_read: bool
    created_at: str


class NotificationListResponse(BaseModel):
    items: list[NotificationItem]
    unread_count: int
    page: int
    page_size: int
    total: int