from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_session
from plugins.notifications.schemas import Notification, NotificationResponse

router = APIRouter()

# -----------------------------
# Health check
# -----------------------------
@router.get("/health", summary="Health check for notifications plugin")
async def health():
    return {"ok": True, "plugin": "notifications"}

# -----------------------------
# Fetch notifications
# -----------------------------
@router.get("/", response_model=NotificationResponse, summary="Fetch notifications")
async def list_notifications(
    db: AsyncSession = Depends(get_session),
    user_id: int = Query(..., description="ID of the user"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of notifications")
):
    """
    Fetch recent notifications for a given user.
    """
    # Placeholder: Replace with actual DB query
    notifications = [
        Notification(id=1, user_id=user_id, type="email", message="Welcome!", read=False),
        Notification(id=2, user_id=user_id, type="in_app", message="You have a new message", read=False)
    ][:limit]

    return NotificationResponse(notifications=notifications)


# -----------------------------
# Send notifications via channels (stubs)
# -----------------------------
@router.post("/send/sms")
async def send_sms(phone: str, message: str):
    print(f"[SMS] to {phone}: {message}")
    return {"detail": "sent"}


@router.post("/send/email")
async def send_email(to: str, subject: str, body: str):
    print(f"[Email] to {to}: {subject}")
    return {"detail": "sent"}


@router.post("/send/push")
async def send_push(token: str, title: str, body: str):
    print(f"[Push] to {token}: {title}")
    return {"detail": "sent"}


@router.post("/send/telegram")
async def send_telegram(chat_id: str, message: str):
    print(f"[Telegram] to {chat_id}: {message}")
    return {"detail": "sent"}


@router.post("/send/whatsapp")
async def send_whatsapp(phone: str, message: str):
    print(f"[WhatsApp] to {phone}: {message}")
    return {"detail": "sent"}