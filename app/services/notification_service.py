"""
Notification service — in-app notifications only.

Crée des entrées dans la table `notifications`.
Les push FCM sont désactivés (pas de firebase-admin).
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from ..models.notification import Notification, NotificationType
from ..models.user import User

logger = logging.getLogger(__name__)


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
    _create_notification(
        db, teacher.id,
        NotificationType.STUDENT_FEEDBACK_HARD,
        "Tâche difficile 😓",
        f"{student_name} a trouvé « {task_title} » très difficile",
        related_task_id=task_id,
    )


def notify_teacher_task_missed(
    db: Session,
    teacher: User,
    student_name: str,
    task_title: str,
    task_id: uuid.UUID,
) -> None:
    _create_notification(
        db, teacher.id,
        NotificationType.TASK_MISSED,
        "Tâche manquée ⚠️",
        f"{student_name} n'a pas effectué « {task_title} »",
        related_task_id=task_id,
    )


def notify_student_streak_at_risk(
    db: Session,
    student: User,
    current_streak: int,
) -> None:
    _create_notification(
        db, student.id,
        NotificationType.STREAK_AT_RISK,
        "Ton streak est en danger ! 🔥",
        f"Tu as un streak de {current_streak} jours — complète une tâche avant minuit !",
    )


def notify_student_streak_broken(
    db: Session,
    student: User,
) -> None:
    _create_notification(
        db, student.id,
        NotificationType.STREAK_BROKEN,
        "Streak perdu 💔",
        "Ton streak a été réinitialisé. Recommence dès aujourd'hui !",
    )


def notify_student_joker_low(
    db: Session,
    student: User,
    jokers_left: int,
) -> None:
    _create_notification(
        db, student.id,
        NotificationType.JOKER_LOW,
        "Joker presque épuisé 🃏",
        f"Il te reste {jokers_left} joker(s) ce mois-ci — utilise-les avec soin.",
    )


def notify_student_new_task(
    db: Session,
    student: User,
    task_title: str,
    task_id: uuid.UUID,
) -> None:
    _create_notification(
        db, student.id,
        NotificationType.NEW_TASK_ASSIGNED,
        "Nouvelle tâche assignée 📚",
        f"Ton professeur t'a assigné : « {task_title} »",
        related_task_id=task_id,
    )
