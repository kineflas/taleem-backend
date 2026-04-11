"""
Autonomous Learning routers — Neuroscience-based Quran vocabulary acquisition.

3 endpoint groups:
  /learn/...              — Public content (any authenticated user)
  /student/learn/...      — Student progress, SRS, exercises
  /learn/audio/...        — Audio proxy (public)

Registered in main.py as separate routers.
"""
import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from ..core.dependencies import CurrentUser, DB, StudentUser
from ..models.autonomous_learning import (
    QuranWord, ArabicRoot, QuranChunk,
    StudentModuleProgress, LeitnerCard, ExerciseSession, ExerciseAttempt,
    AutonomousModule, ModulePhase, WordCategory, ChunkLevel,
)
from ..models.user import User, UserRole
from ..schemas.autonomous_learning import (
    QuranWordOut, ArabicRootOut, QuranChunkOut,
    LeitnerCardOut, SRSStatsOut, ModuleProgressOut,
    ExerciseSessionOut, ExerciseAttemptOut,
    ReviewCardRequest, ExerciseAttemptCreate, StartSessionRequest,
    FlashRecallExercise, VerseScanResult,
)
from ..services.leitner_service import (
    initialize_cards_for_student, get_due_cards, review_card,
    get_student_srs_stats, update_module_progress,
)


# ══════════════════════════════════════════════════════════════════════════════
# Public content router — /learn
# ══════════════════════════════════════════════════════════════════════════════
content_router = APIRouter(prefix="/learn", tags=["Autonomous Learning — Content"])


@content_router.get("/words", response_model=list[QuranWordOut])
def list_words(
    current_user: CurrentUser,
    db: DB,
    module: Optional[int] = Query(None, ge=1, le=5),
    category: Optional[WordCategory] = None,
):
    """List all QuranWords with optional filters by module (1-5) or category."""
    q = db.query(QuranWord)

    if module is not None:
        q = q.filter(QuranWord.module == module)

    if category is not None:
        q = q.filter(QuranWord.category == category)

    return q.order_by(QuranWord.rank).all()


@content_router.get("/words/{word_id}", response_model=QuranWordOut)
def get_word(word_id: uuid.UUID, current_user: CurrentUser, db: DB):
    """Get a single Quran word by ID."""
    word = db.query(QuranWord).filter(QuranWord.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Mot introuvable")
    return word


@content_router.get("/roots", response_model=list[ArabicRootOut])
def list_roots(current_user: CurrentUser, db: DB):
    """List all Arabic roots."""
    return db.query(ArabicRoot).order_by(ArabicRoot.rank).all()


@content_router.get("/roots/{root_id}", response_model=ArabicRootOut)
def get_root(root_id: uuid.UUID, current_user: CurrentUser, db: DB):
    """Get a single Arabic root with its derivations."""
    root = db.query(ArabicRoot).filter(ArabicRoot.id == root_id).first()
    if not root:
        raise HTTPException(status_code=404, detail="Racine introuvable")
    return root


@content_router.get("/chunks", response_model=list[QuranChunkOut])
def list_chunks(
    current_user: CurrentUser,
    db: DB,
    level: Optional[ChunkLevel] = None,
):
    """List all Quran chunks with optional filter by level (PAIR/TRIPLET/SEGMENT)."""
    q = db.query(QuranChunk)

    if level is not None:
        q = q.filter(QuranChunk.level == level)

    return q.order_by(QuranChunk.rank).all()


@content_router.get("/chunks/{chunk_id}", response_model=QuranChunkOut)
def get_chunk(chunk_id: uuid.UUID, current_user: CurrentUser, db: DB):
    """Get a single Quran chunk by ID."""
    chunk = db.query(QuranChunk).filter(QuranChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk introuvable")
    return chunk


@content_router.get("/audio/{surah_number}/{verse_number}")
def get_audio(
    surah_number: int,
    verse_number: int,
    current_user: CurrentUser,
    reciter: str = "Alafasy_128kbps",
):
    """
    Proxy/redirect to EveryAyah API.
    Default reciter: Mishary Rashid Alafasy (Alafasy_128kbps)
    Format: https://everyayah.com/data/{reciter}/{surah:03d}{verse:03d}.mp3
    """
    if surah_number < 1 or surah_number > 114:
        raise HTTPException(status_code=400, detail="Numéro de sourate invalide")
    if verse_number < 1 or verse_number > 286:
        raise HTTPException(status_code=400, detail="Numéro de verset invalide")

    audio_url = (
        f"https://everyayah.com/data/{reciter}/"
        f"{surah_number:03d}{verse_number:03d}.mp3"
    )

    return {"url": audio_url}


# ══════════════════════════════════════════════════════════════════════════════
# Student Learning router — /student/learn
# ══════════════════════════════════════════════════════════════════════════════
student_learn_router = APIRouter(
    prefix="/student/learn", tags=["Student — Autonomous Learning"]
)


@student_learn_router.get("/modules", response_model=list[ModuleProgressOut])
def get_student_modules(student: StudentUser, db: DB):
    """
    Get student's progress for all 5 modules.
    Auto-creates if needed. Module 1 always unlocked.
    """
    modules = []

    for m in range(1, 6):
        prog = db.query(StudentModuleProgress).filter(
            StudentModuleProgress.student_id == student.id,
            StudentModuleProgress.module == m,
        ).first()

        if not prog:
            # Auto-create module
            is_unlocked = (m == 1)  # Only module 1 unlocked initially
            prog = StudentModuleProgress(
                student_id=student.id,
                module=m,
                is_unlocked=is_unlocked,
                current_phase=1,
            )
            db.add(prog)

        modules.append(ModuleProgressOut.model_validate(prog))

    db.commit()
    return modules


@student_learn_router.post(
    "/modules/{module}/start",
    response_model=ModuleProgressOut,
    status_code=status.HTTP_201_CREATED,
)
def start_module(module: int, student: StudentUser, db: DB):
    """Start a module (set started_at, initialize Leitner cards)."""
    if module < 1 or module > 5:
        raise HTTPException(status_code=400, detail="Module invalide (1-5)")

    prog = db.query(StudentModuleProgress).filter(
        StudentModuleProgress.student_id == student.id,
        StudentModuleProgress.module == module,
    ).first()

    if not prog:
        raise HTTPException(status_code=404, detail="Module non trouvée")

    if not prog.is_unlocked:
        raise HTTPException(status_code=403, detail="Module non déverrouillée")

    if prog.started_at:
        raise HTTPException(status_code=400, detail="Module déjà commencée")

    now = datetime.now(timezone.utc)
    prog.started_at = now

    # Initialize Leitner cards for all words in this module
    words = db.query(QuranWord).filter(QuranWord.module == module).all()
    initialize_cards_for_student(db, student.id, words)

    db.commit()
    db.refresh(prog)
    return ModuleProgressOut.model_validate(prog)


@student_learn_router.get(
    "/modules/{module}/progress",
    response_model=ModuleProgressOut,
)
def get_module_progress(module: int, student: StudentUser, db: DB):
    """Get detailed progress for one module."""
    if module < 1 or module > 5:
        raise HTTPException(status_code=400, detail="Module invalide (1-5)")

    prog = db.query(StudentModuleProgress).filter(
        StudentModuleProgress.student_id == student.id,
        StudentModuleProgress.module == module,
    ).first()

    if not prog:
        raise HTTPException(status_code=404, detail="Module non trouvée")

    return ModuleProgressOut.model_validate(prog)


@student_learn_router.get("/srs/due", response_model=list[LeitnerCardOut])
def get_due_srs_cards(
    student: StudentUser,
    db: DB,
    limit: int = Query(20, ge=1, le=100),
):
    """
    Get due Leitner cards for review.
    Cards are due when next_review_date <= today.
    """
    from datetime import date

    today = date.today()
    cards = get_due_cards(db, student.id, today, limit)

    return [LeitnerCardOut.model_validate(c) for c in cards]


@student_learn_router.post("/srs/review", response_model=LeitnerCardOut)
def review_srs_card(
    body: ReviewCardRequest,
    student: StudentUser,
    db: DB,
):
    """
    Review a Leitner card.
    Body: card_id + is_correct
    Updates card and module progress.
    """
    card = db.query(LeitnerCard).filter(
        LeitnerCard.id == body.card_id,
        LeitnerCard.student_id == student.id,
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Carte introuvable")

    word = db.query(QuranWord).filter(QuranWord.id == card.word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Mot introuvable")

    # Review the card
    updated_card = review_card(db, card, body.is_correct)

    # Update module progress
    update_module_progress(db, student.id, word.module)

    db.commit()
    db.refresh(updated_card)
    return LeitnerCardOut.model_validate(updated_card)


@student_learn_router.get("/srs/stats", response_model=SRSStatsOut)
def get_srs_statistics(student: StudentUser, db: DB):
    """Get SRS statistics across all modules."""
    stats = get_student_srs_stats(db, student.id)
    return SRSStatsOut.model_validate(stats)


@student_learn_router.post(
    "/sessions",
    response_model=ExerciseSessionOut,
    status_code=status.HTTP_201_CREATED,
)
def start_exercise_session(
    body: StartSessionRequest,
    student: StudentUser,
    db: DB,
):
    """
    Start an exercise session.
    Body: module (1-5), phase (1-3)
    Returns session_id.
    """
    if body.module < 1 or body.module > 5:
        raise HTTPException(status_code=400, detail="Module invalide (1-5)")
    if body.phase < 1 or body.phase > 3:
        raise HTTPException(status_code=400, detail="Phase invalide (1-3)")

    session = ExerciseSession(
        student_id=student.id,
        module=body.module,
        phase=body.phase,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return ExerciseSessionOut.model_validate(session)


@student_learn_router.post(
    "/sessions/{session_id}/attempt",
    response_model=ExerciseAttemptOut,
    status_code=status.HTTP_201_CREATED,
)
def record_exercise_attempt(
    session_id: uuid.UUID,
    body: ExerciseAttemptCreate,
    student: StudentUser,
    db: DB,
):
    """Record an exercise attempt within a session."""
    session = db.query(ExerciseSession).filter(
        ExerciseSession.id == session_id,
        ExerciseSession.student_id == student.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")

    if session.ended_at:
        raise HTTPException(status_code=400, detail="Session terminée")

    attempt = ExerciseAttempt(
        session_id=session_id,
        student_id=student.id,
        exercise_type=body.exercise_type,
        word_id=body.word_id,
        chunk_id=body.chunk_id,
        root_id=body.root_id,
        surah_number=body.surah_number,
        verse_number=body.verse_number,
        is_correct=body.is_correct,
        response_time_ms=body.response_time_ms,
        shown_data=body.shown_data,
        answer_data=body.answer_data,
    )
    db.add(attempt)

    # Update session stats
    session.total_exercises += 1
    if body.is_correct:
        session.correct_count += 1

    db.commit()
    db.refresh(attempt)

    return ExerciseAttemptOut.model_validate(attempt)


@student_learn_router.patch(
    "/sessions/{session_id}/end",
    response_model=ExerciseSessionOut,
)
def end_exercise_session(
    session_id: uuid.UUID,
    student: StudentUser,
    db: DB,
):
    """End session and calculate duration."""
    session = db.query(ExerciseSession).filter(
        ExerciseSession.id == session_id,
        ExerciseSession.student_id == student.id,
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable")

    if session.ended_at:
        raise HTTPException(status_code=400, detail="Session déjà terminée")

    now = datetime.now(timezone.utc)
    session.ended_at = now

    # Calculate duration in seconds
    duration = (now - session.started_at).total_seconds()
    session.duration_seconds = int(duration)

    db.commit()
    db.refresh(session)

    return ExerciseSessionOut.model_validate(session)


@student_learn_router.get(
    "/exercises/flash-recall",
    response_model=FlashRecallExercise,
)
def generate_flash_recall_exercise(
    student: StudentUser,
    db: DB,
    word_id: uuid.UUID = Query(...),
):
    """
    Generate Flash & Recall QCM exercise.
    Query: word_id
    Returns: word + 3 random distractors from same module.
    """
    word = db.query(QuranWord).filter(QuranWord.id == word_id).first()

    if not word:
        raise HTTPException(status_code=404, detail="Mot introuvable")

    # Get 3 random distractors from the same module, different from target
    distractors = db.query(QuranWord).filter(
        QuranWord.module == word.module,
        QuranWord.id != word_id,
    ).all()

    if len(distractors) < 3:
        raise HTTPException(
            status_code=400,
            detail="Pas assez de mots pour générer les distracteurs",
        )

    selected_distractors = random.sample(distractors, 3)

    return FlashRecallExercise(
        word=QuranWordOut.model_validate(word),
        distractors=[
            QuranWordOut.model_validate(d) for d in selected_distractors
        ],
    )


@student_learn_router.get(
    "/exercises/root-intruder",
    response_model=dict,
)
def generate_root_intruder_exercise(
    student: StudentUser,
    db: DB,
    root_id: uuid.UUID = Query(...),
):
    """
    Generate "Find the intruder" exercise.
    Query: root_id
    Returns: 3 words from the root + 1 intruder word from different root.
    """
    root = db.query(ArabicRoot).filter(ArabicRoot.id == root_id).first()

    if not root:
        raise HTTPException(status_code=404, detail="Racine introuvable")

    # Get words from this root
    root_words = db.query(QuranWord).filter(
        QuranWord.root_id == root_id
    ).all()

    if len(root_words) < 3:
        raise HTTPException(
            status_code=400,
            detail="Pas assez de mots de cette racine",
        )

    selected_root_words = random.sample(root_words, min(3, len(root_words)))

    # Get an intruder from a different root
    intruder = db.query(QuranWord).filter(
        QuranWord.root_id != root_id,
        QuranWord.root_id != None,
    ).order_by(lambda: func.random()).first()

    if not intruder:
        raise HTTPException(
            status_code=400,
            detail="Pas d'intrus disponible",
        )

    # Mix and shuffle
    all_words = selected_root_words + [intruder]
    random.shuffle(all_words)

    return {
        "root": ArabicRootOut.model_validate(root),
        "words": [QuranWordOut.model_validate(w) for w in all_words],
        "intruder_id": intruder.id,
    }


@student_learn_router.get(
    "/exercises/verse-scan",
    response_model=VerseScanResult,
)
def generate_verse_scan_exercise(
    student: StudentUser,
    db: DB,
    surah_number: int = Query(..., ge=1, le=114),
    verse_number: int = Query(..., ge=1, le=286),
):
    """
    Get a verse for scanning exercise.
    Query: surah_number, verse_number
    Returns: verse text + list of known word_ids from student's vocabulary.
    """
    from ..models.quran import Verse  # Import Verse model if available

    # Placeholder: in real implementation, fetch from Verse model
    # For now, we'll return a structure that frontend can populate

    # Get student's known words (Box 3-5 cards or completed)
    known_cards = db.query(LeitnerCard).filter(
        LeitnerCard.student_id == student.id,
        LeitnerCard.box >= 3,
    ).all()

    known_word_ids = [card.word_id for card in known_cards]

    return VerseScanResult(
        surah_number=surah_number,
        verse_number=verse_number,
        verse_text="",  # Populated by frontend or Quran API
        known_word_ids=known_word_ids,
    )
