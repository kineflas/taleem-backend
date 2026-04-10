"""
Curriculum Engine routers — 3 groups:

  /curriculum/...          — static content (any authenticated user)
  /student/curriculum/...  — student progress & enrollments
  /teacher/curriculum/...  — teacher management & submission review

Registered in main.py as separate routers.
"""
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..core.dependencies import CurrentUser, DB, StudentUser, TeacherUser
from ..models.curriculum import (
    CurriculumProgram, CurriculumUnit, CurriculumItem,
    StudentEnrollment, StudentItemProgress, StudentSubmission,
    EnrollmentMode, SubmissionStatus,
)
from ..models.notification import Notification, NotificationType
from ..models.user import TeacherStudentLink, User
from ..schemas.curriculum import (
    CurriculumProgramOut, CurriculumProgramDetailOut,
    CurriculumUnitOut, CurriculumUnitDetailOut, CurriculumItemOut,
    EnrollRequest, TeacherEnrollRequest, EnrollmentOut,
    EnrollmentProgressOut, UnitProgressOut, ItemProgressOut,
    CompleteItemRequest, ValidateItemRequest,
    SubmissionCreate, SubmissionReviewRequest, SubmissionOut,
)
from ..services.notification_service import _create_notification

# ══════════════════════════════════════════════════════════════════════════════
# Static content router
# ══════════════════════════════════════════════════════════════════════════════
content_router = APIRouter(prefix="/curriculum", tags=["Curriculum — Content"])


@content_router.get("/programs", response_model=list[CurriculumProgramOut])
def list_programs(current_user: CurrentUser, db: DB):
    return db.query(CurriculumProgram).filter(
        CurriculumProgram.is_active == True
    ).order_by(CurriculumProgram.sort_order).all()


@content_router.get("/programs/{curriculum_type}", response_model=CurriculumProgramDetailOut)
def get_program(curriculum_type: str, current_user: CurrentUser, db: DB):
    program = db.query(CurriculumProgram).filter(
        CurriculumProgram.curriculum_type == curriculum_type.upper()
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme introuvable")
    return program


@content_router.get("/programs/{curriculum_type}/units", response_model=list[CurriculumUnitOut])
def list_units(curriculum_type: str, current_user: CurrentUser, db: DB):
    program = db.query(CurriculumProgram).filter(
        CurriculumProgram.curriculum_type == curriculum_type.upper()
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme introuvable")
    return program.units


@content_router.get("/units/{unit_id}", response_model=CurriculumUnitDetailOut)
def get_unit(unit_id: uuid.UUID, current_user: CurrentUser, db: DB):
    unit = db.query(CurriculumUnit).filter(CurriculumUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unité introuvable")
    return unit


@content_router.get("/units/{unit_id}/items", response_model=list[CurriculumItemOut])
def list_items(unit_id: uuid.UUID, current_user: CurrentUser, db: DB):
    unit = db.query(CurriculumUnit).filter(CurriculumUnit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unité introuvable")
    return unit.items


@content_router.get("/items/{item_id}", response_model=CurriculumItemOut)
def get_item(item_id: uuid.UUID, current_user: CurrentUser, db: DB):
    item = db.query(CurriculumItem).filter(CurriculumItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Élément introuvable")
    return item


# ══════════════════════════════════════════════════════════════════════════════
# Student curriculum router
# ══════════════════════════════════════════════════════════════════════════════
student_curriculum_router = APIRouter(
    prefix="/student/curriculum", tags=["Student — Curriculum"]
)


def _build_enrollment_progress(
    db: Session, enrollment: StudentEnrollment
) -> EnrollmentProgressOut:
    units = enrollment.program.units
    all_progress = {
        p.curriculum_item_id: p
        for p in db.query(StudentItemProgress)
        .filter(StudentItemProgress.enrollment_id == enrollment.id)
        .all()
    }

    unit_progresses = []
    total_items = 0
    total_completed = 0

    for unit in units:
        items_progress = []
        unit_completed = 0
        for item in unit.items:
            prog = all_progress.get(item.id)
            items_progress.append(ItemProgressOut(
                id=prog.id if prog else uuid.uuid4(),  # virtual if not started
                curriculum_item_id=item.id,
                is_completed=prog.is_completed if prog else False,
                completed_at=prog.completed_at if prog else None,
                mastery_level=prog.mastery_level if prog else None,
                attempt_count=prog.attempt_count if prog else 0,
                teacher_validated=prog.teacher_validated if prog else False,
                teacher_validated_at=prog.teacher_validated_at if prog else None,
            ))
            if prog and prog.is_completed:
                unit_completed += 1

        total_items += len(unit.items)
        total_completed += unit_completed
        pct = (unit_completed / len(unit.items) * 100) if unit.items else 0

        unit_progresses.append(UnitProgressOut(
            unit=CurriculumUnitOut.model_validate(unit),
            total_items=len(unit.items),
            completed_items=unit_completed,
            completion_pct=round(pct, 1),
            items_progress=items_progress,
        ))

    overall_pct = (total_completed / total_items * 100) if total_items else 0

    return EnrollmentProgressOut(
        enrollment=EnrollmentOut.model_validate(enrollment),
        total_items=total_items,
        completed_items=total_completed,
        completion_pct=round(overall_pct, 1),
        units=unit_progresses,
    )


@student_curriculum_router.get("/enrollments", response_model=list[EnrollmentOut])
def list_enrollments(student: StudentUser, db: DB):
    return (
        db.query(StudentEnrollment)
        .filter(StudentEnrollment.student_id == student.id, StudentEnrollment.is_active == True)
        .all()
    )


@student_curriculum_router.post(
    "/enroll", response_model=EnrollmentOut, status_code=status.HTTP_201_CREATED
)
def enroll_autonomous(body: EnrollRequest, student: StudentUser, db: DB):
    program = db.query(CurriculumProgram).filter(
        CurriculumProgram.id == body.curriculum_program_id,
        CurriculumProgram.is_active == True,
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme introuvable")

    existing = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == student.id,
        StudentEnrollment.curriculum_program_id == body.curriculum_program_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Déjà inscrit à ce programme")

    # Set first unit/item as current
    first_unit = program.units[0] if program.units else None
    first_item = first_unit.items[0] if first_unit and first_unit.items else None

    enrollment = StudentEnrollment(
        student_id=student.id,
        curriculum_program_id=body.curriculum_program_id,
        mode=EnrollmentMode.STUDENT_AUTONOMOUS,
        target_end_at=body.target_end_at,
        current_unit_id=first_unit.id if first_unit else None,
        current_item_id=first_item.id if first_item else None,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@student_curriculum_router.get(
    "/enrollments/{enrollment_id}/progress", response_model=EnrollmentProgressOut
)
def get_enrollment_progress(enrollment_id: uuid.UUID, student: StudentUser, db: DB):
    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.id == enrollment_id,
        StudentEnrollment.student_id == student.id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscription introuvable")
    return _build_enrollment_progress(db, enrollment)


@student_curriculum_router.get("/enrollments/{enrollment_id}/next-item")
def next_item(enrollment_id: uuid.UUID, student: StudentUser, db: DB):
    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.id == enrollment_id,
        StudentEnrollment.student_id == student.id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscription introuvable")

    completed_ids = {
        p.curriculum_item_id
        for p in db.query(StudentItemProgress)
        .filter(
            StudentItemProgress.enrollment_id == enrollment.id,
            StudentItemProgress.is_completed == True,
        )
        .all()
    }

    for unit in enrollment.program.units:
        for item in unit.items:
            if item.id not in completed_ids:
                return {
                    "unit": CurriculumUnitOut.model_validate(unit),
                    "item": CurriculumItemOut.model_validate(item),
                }

    return {"unit": None, "item": None, "message": "Programme complété 🎉"}


@student_curriculum_router.post("/items/{item_id}/complete", status_code=status.HTTP_201_CREATED)
def complete_item(
    item_id: uuid.UUID,
    body: CompleteItemRequest,
    student: StudentUser,
    db: DB,
    enrollment_id: uuid.UUID = None,
):
    # Find enrollment
    if enrollment_id:
        enrollment = db.query(StudentEnrollment).filter(
            StudentEnrollment.id == enrollment_id,
            StudentEnrollment.student_id == student.id,
        ).first()
    else:
        # Find enrollment via item → unit → program
        item = db.query(CurriculumItem).filter(CurriculumItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Élément introuvable")
        enrollment = db.query(StudentEnrollment).filter(
            StudentEnrollment.student_id == student.id,
            StudentEnrollment.curriculum_program_id == item.unit.curriculum_program_id,
        ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscription introuvable")

    # Upsert progress
    prog = db.query(StudentItemProgress).filter(
        StudentItemProgress.enrollment_id == enrollment.id,
        StudentItemProgress.curriculum_item_id == item_id,
    ).first()

    now = datetime.now(timezone.utc)

    if prog:
        prog.is_completed = True
        prog.completed_at = now
        prog.mastery_level = body.mastery_level or prog.mastery_level
        prog.attempt_count += 1
        prog.last_attempt_at = now
    else:
        prog = StudentItemProgress(
            enrollment_id=enrollment.id,
            student_id=student.id,
            curriculum_item_id=item_id,
            is_completed=True,
            completed_at=now,
            mastery_level=body.mastery_level,
            attempt_count=1,
            last_attempt_at=now,
        )
        db.add(prog)

    # Advance enrollment pointer
    enrollment.current_item_id = item_id
    enrollment.updated_at = now

    db.commit()
    db.refresh(prog)
    return ItemProgressOut.model_validate(prog)


@student_curriculum_router.post(
    "/submissions", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED
)
def create_submission(body: SubmissionCreate, student: StudentUser, db: DB):
    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.id == body.enrollment_id,
        StudentEnrollment.student_id == student.id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscription introuvable")

    submission = StudentSubmission(
        student_id=student.id,
        teacher_id=enrollment.teacher_id,
        enrollment_id=body.enrollment_id,
        curriculum_item_id=body.curriculum_item_id,
        audio_url=body.audio_url,
        text_content=body.text_content,
    )
    db.add(submission)
    db.flush()

    # Notify teacher
    if enrollment.teacher_id:
        teacher = db.query(User).filter(User.id == enrollment.teacher_id).first()
        if teacher:
            _create_notification(
                db, teacher.id,
                NotificationType.SUBMISSION_RECEIVED,
                "Nouvelle soumission 🎤",
                f"{student.full_name} a envoyé un enregistrement",
            )

    db.commit()
    db.refresh(submission)
    return submission


@student_curriculum_router.get("/submissions", response_model=list[SubmissionOut])
def list_my_submissions(student: StudentUser, db: DB):
    return (
        db.query(StudentSubmission)
        .filter(StudentSubmission.student_id == student.id)
        .order_by(StudentSubmission.created_at.desc())
        .limit(100)
        .all()
    )


# ══════════════════════════════════════════════════════════════════════════════
# Teacher curriculum router
# ══════════════════════════════════════════════════════════════════════════════
teacher_curriculum_router = APIRouter(
    prefix="/teacher/curriculum", tags=["Teacher — Curriculum"]
)


@teacher_curriculum_router.get(
    "/students/{student_id}/enrollments", response_model=list[EnrollmentOut]
)
def student_enrollments(student_id: uuid.UUID, teacher: TeacherUser, db: DB):
    # Verify link
    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher.id,
        TeacherStudentLink.student_id == student_id,
        TeacherStudentLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    return (
        db.query(StudentEnrollment)
        .filter(
            StudentEnrollment.student_id == student_id,
            StudentEnrollment.is_active == True,
        )
        .all()
    )


@teacher_curriculum_router.post(
    "/students/{student_id}/enroll",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
)
def teacher_enroll_student(
    student_id: uuid.UUID, body: TeacherEnrollRequest, teacher: TeacherUser, db: DB
):
    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher.id,
        TeacherStudentLink.student_id == student_id,
        TeacherStudentLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    program = db.query(CurriculumProgram).filter(
        CurriculumProgram.id == body.curriculum_program_id,
        CurriculumProgram.is_active == True,
    ).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programme introuvable")

    existing = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == student_id,
        StudentEnrollment.curriculum_program_id == body.curriculum_program_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Élève déjà inscrit à ce programme")

    first_unit = program.units[0] if program.units else None
    first_item = first_unit.items[0] if first_unit and first_unit.items else None

    enrollment = StudentEnrollment(
        student_id=student_id,
        curriculum_program_id=body.curriculum_program_id,
        teacher_id=teacher.id,
        mode=EnrollmentMode.TEACHER_ASSIGNED,
        target_end_at=body.target_end_at,
        current_unit_id=first_unit.id if first_unit else None,
        current_item_id=first_item.id if first_item else None,
    )
    db.add(enrollment)
    db.flush()

    # Notify student
    student = db.query(User).filter(User.id == student_id).first()
    if student:
        _create_notification(
            db, student.id,
            NotificationType.NEW_TASK_ASSIGNED,
            f"Nouveau programme : {program.title_fr}",
            f"{teacher.full_name} t'a inscrit(e) au programme {program.title_fr}",
        )
        if student.fcm_token:
            from ..services.notification_service import _send_push
            _send_push(
                student.fcm_token,
                f"Nouveau programme : {program.title_fr}",
                f"{teacher.full_name} t'a inscrit(e) à ce programme",
            )

    db.commit()
    db.refresh(enrollment)
    return enrollment


@teacher_curriculum_router.get(
    "/students/{student_id}/progress/{enrollment_id}",
    response_model=EnrollmentProgressOut,
)
def student_enrollment_progress(
    student_id: uuid.UUID, enrollment_id: uuid.UUID, teacher: TeacherUser, db: DB
):
    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher.id,
        TeacherStudentLink.student_id == student_id,
        TeacherStudentLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.id == enrollment_id,
        StudentEnrollment.student_id == student_id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscription introuvable")

    return _build_enrollment_progress(db, enrollment)


@teacher_curriculum_router.get("/submissions", response_model=list[SubmissionOut])
def list_submissions(
    teacher: TeacherUser,
    db: DB,
    status_filter: SubmissionStatus | None = None,
):
    q = db.query(StudentSubmission).filter(StudentSubmission.teacher_id == teacher.id)
    if status_filter:
        q = q.filter(StudentSubmission.status == status_filter)
    return q.order_by(StudentSubmission.created_at.desc()).limit(200).all()


@teacher_curriculum_router.get("/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: uuid.UUID, teacher: TeacherUser, db: DB):
    sub = db.query(StudentSubmission).filter(
        StudentSubmission.id == submission_id,
        StudentSubmission.teacher_id == teacher.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Soumission introuvable")
    return sub


@teacher_curriculum_router.patch(
    "/submissions/{submission_id}/review", response_model=SubmissionOut
)
def review_submission(
    submission_id: uuid.UUID,
    body: SubmissionReviewRequest,
    teacher: TeacherUser,
    db: DB,
):
    sub = db.query(StudentSubmission).filter(
        StudentSubmission.id == submission_id,
        StudentSubmission.teacher_id == teacher.id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Soumission introuvable")

    sub.status = body.status
    sub.teacher_feedback = body.teacher_feedback
    sub.reviewed_at = datetime.now(timezone.utc)
    db.flush()

    # Notify student
    student = db.query(User).filter(User.id == sub.student_id).first()
    if student:
        verdict = "approuvée ✅" if body.status == SubmissionStatus.APPROVED else "à améliorer 🔄"
        _create_notification(
            db, student.id,
            NotificationType.SUBMISSION_REVIEWED,
            f"Soumission {verdict}",
            body.teacher_feedback or f"Ton enseignant a évalué ta soumission : {verdict}",
        )
        if student.fcm_token:
            from ..services.notification_service import _send_push
            _send_push(student.fcm_token, f"Soumission {verdict}", body.teacher_feedback or "")

    db.commit()
    db.refresh(sub)
    return sub


@teacher_curriculum_router.post(
    "/items/{item_id}/validate", status_code=status.HTTP_204_NO_CONTENT
)
def validate_item_for_student(
    item_id: uuid.UUID, body: ValidateItemRequest, teacher: TeacherUser, db: DB
):
    # Verify teacher-student relationship
    link = db.query(TeacherStudentLink).filter(
        TeacherStudentLink.teacher_id == teacher.id,
        TeacherStudentLink.student_id == body.student_id,
        TeacherStudentLink.is_active == True,
    ).first()
    if not link:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    enrollment = db.query(StudentEnrollment).filter(
        StudentEnrollment.student_id == body.student_id,
        StudentEnrollment.teacher_id == teacher.id,
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscription introuvable")

    now = datetime.now(timezone.utc)
    prog = db.query(StudentItemProgress).filter(
        StudentItemProgress.enrollment_id == enrollment.id,
        StudentItemProgress.curriculum_item_id == item_id,
    ).first()

    if prog:
        prog.teacher_validated = True
        prog.teacher_validated_at = now
        if not prog.is_completed:
            prog.is_completed = True
            prog.completed_at = now
    else:
        prog = StudentItemProgress(
            enrollment_id=enrollment.id,
            student_id=body.student_id,
            curriculum_item_id=item_id,
            is_completed=True,
            completed_at=now,
            teacher_validated=True,
            teacher_validated_at=now,
            mastery_level=3,
        )
        db.add(prog)

    db.commit()
