"""
Push notification service — FCM via firebase-admin.

Spec §5.7:
  - Difficulty = 3 (😓) → immediate push to teacher
  - Streak at risk (hour >= 20, no completion) → push to student
  - Missed task → push to teacher
  - Joker low (1 remaining) → push to student
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from ..models.notification import Notification, NotificationType
from ..models.user import User

logger = logging.getLogger(__name__)

# Firebase Admin is optional — will gracefully degrade if not configured
try:
    import firebase_admin
    from firebase_admin import credentials, messaging

    _firebase_initialized = False

    def _init_firebase(cred_path: str) -> None:
        global _firebase_initialized
        if not _firebase_initialized:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True

except ImportError:
    logger.warning("firebase-admin not installed — push notifications disabled")
    messaging = None  # type: ignore


def _send_push(fcm_token: str, title: str, body: str, data: Optional[dict] = None) -> bool:
    """Send a single FCM push notification. Returns True on success."""
    if messaging is None:
        logger.debug("FCM disabled — would send: %s / %s", title, body)
        return False

    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=fcm_token,
            android=messaging.AndroidConfig(priority="high"),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default")
                )
            ),
        )
        messaging.send(message)
        return True
    except Exception as exc:
        logger.error("FCM send error: %s", exc)
        return False


def _create_notification(
    db: Session,
    recipient_id: uuid.UUID,
    notif_type: NotificationType,
    title: str,
    body: str,
    related_task_id: Optional[uuid.UUID] = None,
) -> Notification:
    notif = Notification(
        recipient_id=recipient_id,
        type=notif_type,
        title=title,
        body=body,
        related_task_id=related_task_id,
    )
    db.add(notif)
    return notif


# ── Public API ──────────────────────────────────────────────────────────────

def notify_teacher_difficulty(
    db: Session,
    teacher: User,
    student_name: str,
    task_title: str,
    task_id: uuid.UUID,
) -> None:
    """Spec §5.7 — immediate push when student marks difficulty = 3 (😓)."""
    title = "Tâche difficile 😓"
    body = f"{student_name} a trouvé « {task_title} » très difficile"

    notif = _create_notification(
        db, teacher.id,
        NotificationType.STUDENT_FEEDBACK_HARD,
        title, body,
        related_task_id=task_id,
    )
    db.flush()

    if teacher.fcm_token:
        _send_push(teacher.fcm_token, title, body, {"task_id": str(task_id)})


def notify_teacher_task_missed(
    db: Session,
    teacher: User,
    student_name: str,
    task_title: str,
    task_id: uuid.UUID,
) -> None:
    title = "Tâche manquée ⚠️"
    body = f"{student_name} n'a pas effectué « {task_title} »"

    notif = _create_notification(
        db, teacher.id,
        NotificationType.TASK_MISSED,
        title, body,
        related_task_id=task_id,
    )
    db.flush()

    if teacher.fcm_token:
        _send_push(teacher.fcm_token, title, body, {"task_id": str(task_id)})


def notify_student_streak_at_risk(
    db: Session,
    student: User,
    current_streak: int,
) -> None:
    title = "Ton streak est en danger ! 🔥"
    body = f"Tu as un streak de {current_streak} jours — complète une tâche avant minuit !"

    notif = _create_notification(
        db, student.id,
        NotificationType.STREAK_AT_RISK,
        title, body,
    )
    db.flush()

    if student.fcm_token:
        _send_push(student.fcm_token, title, body, {"current_streak": str(current_streak)})


def notify_student_streak_broken(
    db: Session,
    student: User,
) -> None:
    title = "Streak perdu 💔"
    body = "Ton streak a été réinitialisé. Recommence dès aujourd'hui !"

    notif = _create_notification(
        db, student.id,
        NotificationType.STREAK_BROKEN,
        title, body,
    )
    db.flush()

    if student.fcm_token:
        _send_push(student.fcm_token, title, body)


def notify_student_joker_low(
    db: Session,
    student: User,
    jokers_left: int,
) -> None:
    title = "Joker presque épuisé 🃏"
    body = f"Il te reste {jokers_left} joker(s) ce mois-ci — utilise-les avec soin."

    notif = _create_notification(
        db, student.id,
        NotificationType.JOKER_LOW,
        title, body,
    )
    db.flush()

    if student.fcm_token:
        _send_push(student.fcm_token, title, body, {"jokers_left": str(jokers_left)})


def notify_student_new_task(
    db: Session,
    student: User,
    task_title: str,
    task_id: uuid.UUID,
) -> None:
    title = "Nouvelle tâche assignée 📚"
    body = f"Ton professeur t'a assigné : « {task_title} »"

    notif = _create_notification(
        db, student.id,
        NotificationType.NEW_TASK_ASSIGNED,
        title, body,
        related_task_id=task_id,
    )
    db.flush()

    if student.fcm_token:
        _send_push(student.fcm_token, title, body, {"task_id": str(task_id)})
