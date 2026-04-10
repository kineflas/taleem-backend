"""
Notification endpoints.

Routes:
  GET   /notifications              — list notifications for current user
  PATCH /notifications/{id}/read    — mark one as read
  PATCH /notifications/read-all     — mark all as read
  PUT   /notifications/fcm-token    — register/update FCM device token
"""
import uuid

from fastapi import APIRouter, HTTPException
from ..core.dependencies import CurrentUser, DB
from ..models.notification import Notification
from ..schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(current_user: CurrentUser, db: DB, unread_only: bool = False):
    q = db.query(Notification).filter(Notification.recipient_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    return q.order_by(Notification.created_at.desc()).limit(100).all()


@router.patch("/{notification_id}/read", status_code=204)
def mark_read(notification_id: uuid.UUID, current_user: CurrentUser, db: DB):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification introuvable")
    notif.is_read = True
    db.commit()


@router.patch("/read-all", status_code=204)
def mark_all_read(current_user: CurrentUser, db: DB):
    db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()


@router.put("/fcm-token", status_code=204)
def update_fcm_token(token: str, current_user: CurrentUser, db: DB):
    current_user.fcm_token = token
    db.commit()
