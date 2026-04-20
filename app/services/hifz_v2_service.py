"""
Hifz V2 Service — SRS 7-tier algorithm & Wird composition engine.

Responsibilities:
  - Compose daily Wird (JADID + QARIB + BA'ID blocs)
  - Calculate mastery score updates after exercises
  - Determine SRS tier and next review date
  - Award XP based on performance
"""
import uuid
import logging
from datetime import date, datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from ..models.hifz_master import (
    HifzGoal, VerseProgress, StudentXP, StudentBadge,
    VerseMastery, BadgeType, StudentLevel,
)
from ..models.hifz_v2 import (
    WirdSession, VerseExercise, WirdStatus, ExerciseType,
    SrsTier, SRS_TIERS, tier_from_score, WirdBloc,
)

logger = logging.getLogger(__name__)


# ── XP Constants ─────────────────────────────────────────────────

XP_PER_EXERCISE_CORRECT = 5
XP_PER_EXERCISE_WRONG = 1  # Participation XP
XP_BONUS_PERFECT_VERSE = 20  # 3 stars on a verse
XP_BONUS_TIER_UP = 10
XP_WIRD_COMPLETION = 30


# ── Score Update Constants ───────────────────────────────────────

SCORE_GAIN_EASY = 8    # Easy exercise correct (VRAI_FAUX, MOT_MANQUANT)
SCORE_GAIN_MEDIUM = 12  # Medium exercise correct (PUZZLE, DEBUT_FIN, ECOUTE)
SCORE_GAIN_HARD = 15   # Hard exercise correct (VERSET_MIROIR, DICTEE)
SCORE_LOSS_EASY = -10
SCORE_LOSS_MEDIUM = -15
SCORE_LOSS_HARD = -20

EXERCISE_DIFFICULTY = {
    ExerciseType.VRAI_FAUX: "easy",
    ExerciseType.MOT_MANQUANT: "easy",
    ExerciseType.PUZZLE: "medium",
    ExerciseType.DEBUT_FIN: "medium",
    ExerciseType.ECOUTE: "medium",
    ExerciseType.VERSET_SUIVANT: "medium",
    ExerciseType.DICTEE: "hard",
    ExerciseType.VERSET_MIROIR: "hard",
    # Checkpoint exercises (Phase 2)
    ExerciseType.TARTIB: "medium",
    ExerciseType.TAKAMUL: "medium",
}


# ── Student Titles ───────────────────────────────────────────────

TITLES = [
    {"min_xp": 0,     "fr": "Talib",          "ar": "طالب"},
    {"min_xp": 500,   "fr": "Qari",           "ar": "قارئ"},
    {"min_xp": 2000,  "fr": "Hafiz Mubtadi",  "ar": "حافظ مبتدئ"},
    {"min_xp": 5000,  "fr": "Hafiz",          "ar": "حافظ"},
    {"min_xp": 15000, "fr": "Hafiz Mutqin",   "ar": "حافظ متقن"},
]


def get_title(total_xp: int) -> dict:
    """Get spiritual title based on total XP."""
    title = TITLES[0]
    for t in TITLES:
        if total_xp >= t["min_xp"]:
            title = t
    return title


# ── SRS Functions ────────────────────────────────────────────────

def calculate_next_review_date(tier: SrsTier, from_date: date | None = None) -> date:
    """Calculate next review date based on SRS tier."""
    base = from_date or date.today()
    interval = SRS_TIERS[tier]["interval_days"]
    return base + timedelta(days=interval)


def calculate_stars(score: int) -> int:
    """Calculate stars from mastery score."""
    if score >= 90:
        return 3
    elif score >= 70:
        return 2
    elif score >= 50:
        return 1
    return 0


def get_score_delta(exercise_type: ExerciseType, is_correct: bool) -> int:
    """Get score change for an exercise result."""
    difficulty = EXERCISE_DIFFICULTY.get(exercise_type, "medium")
    if is_correct:
        return {"easy": SCORE_GAIN_EASY, "medium": SCORE_GAIN_MEDIUM, "hard": SCORE_GAIN_HARD}[difficulty]
    else:
        return {"easy": SCORE_LOSS_EASY, "medium": SCORE_LOSS_MEDIUM, "hard": SCORE_LOSS_HARD}[difficulty]


def update_mastery_from_score(score: int) -> str:
    """Map score to backward-compatible VerseMastery (RED/ORANGE/GREEN)."""
    if score >= 70:
        return "GREEN"
    elif score >= 40:
        return "ORANGE"
    return "RED"


# ── Wird Composition ─────────────────────────────────────────────

def compose_wird(
    db: Session,
    student_id: uuid.UUID,
    surah_number: int | None = None,
) -> dict:
    """
    Compose today's Wird for a student.

    Returns dict with:
      - jadid_verses: list of (surah_number, verse_number) for new verses
      - qarib_verses: list of (surah_number, verse_number) for recent review
      - baid_verses: list of (surah_number, verse_number) for distant review
      - reciter_folder: str
      - estimated_minutes: int
    """
    today = date.today()

    # Get active goal (most recent non-completed)
    goal = (
        db.query(HifzGoal)
        .filter(
            HifzGoal.student_id == student_id,
            HifzGoal.is_completed == False,
        )
        .order_by(HifzGoal.started_at.desc())
        .first()
    )

    reciter = "Alafasy_128kbps"
    daily_target = 3  # Default: 3 new verses per day

    if goal:
        reciter = goal.reciter_id
        daily_target = goal.calculated_daily_target or 3

    # ── Determine which surah to use for JADID ──────────────────
    # If the user explicitly chose a surah, use it; otherwise use the active goal
    target_surah = surah_number  # From user selection (Ikhtiar screen)
    target_total_verses = 0

    if target_surah:
        # User chose a specific surah — look up its total verses
        from ..models.quran import Surah
        surah_record = db.query(Surah).filter(Surah.surah_number == target_surah).first()
        if surah_record:
            target_total_verses = surah_record.total_verses
        else:
            # Fallback to known counts (Juz Amma)
            from ..routers.hifz_master import SURAH_VERSE_COUNTS
            if 1 <= target_surah <= len(SURAH_VERSE_COUNTS):
                target_total_verses = SURAH_VERSE_COUNTS[target_surah - 1]
    elif goal:
        target_surah = goal.surah_number
        target_total_verses = goal.total_verses

    # ── JADID: Find new verses to learn ──────────────────────────
    jadid_verses = []
    if target_surah and target_total_verses > 0:
        # Find the last verse the student has progress on for this surah
        last_verse = (
            db.query(func.max(VerseProgress.verse_number))
            .filter(
                VerseProgress.student_id == student_id,
                VerseProgress.surah_number == target_surah,
            )
            .scalar()
        ) or 0

        # Next verses to learn
        for i in range(1, daily_target + 1):
            next_verse = last_verse + i
            if next_verse <= target_total_verses:
                jadid_verses.append({
                    "surah_number": target_surah,
                    "verse_number": next_verse,
                })

    # ── QARIB: Recent verses needing review (J+1 to J+7) ────────
    qarib_cutoff = today + timedelta(days=1)  # Include due today and tomorrow
    qarib_rows = (
        db.query(VerseProgress)
        .filter(
            VerseProgress.student_id == student_id,
            VerseProgress.next_review_date <= qarib_cutoff,
            VerseProgress.mastery_score < 70,  # Not yet SOLIDE
        )
        .order_by(VerseProgress.mastery_score.asc())  # Weakest first
        .limit(10)
        .all()
    )
    qarib_verses = [
        {
            "surah_number": v.surah_number,
            "verse_number": v.verse_number,
            "mastery_score": v.mastery_score,
            "srs_tier": tier_from_score(v.mastery_score).value,
        }
        for v in qarib_rows
    ]

    # ── BA'ID: Distant verses needing consolidation ──────────────
    baid_rows = (
        db.query(VerseProgress)
        .filter(
            VerseProgress.student_id == student_id,
            VerseProgress.next_review_date <= today,
            VerseProgress.mastery_score >= 70,  # SOLIDE or higher
        )
        .order_by(VerseProgress.next_review_date.asc())  # Most overdue first
        .limit(8)
        .all()
    )
    baid_verses = [
        {
            "surah_number": v.surah_number,
            "verse_number": v.verse_number,
            "mastery_score": v.mastery_score,
            "srs_tier": tier_from_score(v.mastery_score).value,
        }
        for v in baid_rows
    ]

    # ── Estimate duration ────────────────────────────────────────
    # JADID: ~10 min per verse (5-step flow)
    # QARIB: ~2 min per verse
    # BA'ID: ~1 min per verse
    estimated_minutes = (
        len(jadid_verses) * 10
        + len(qarib_verses) * 2
        + len(baid_verses) * 1
    )

    return {
        "jadid_verses": jadid_verses,
        "qarib_verses": qarib_verses,
        "baid_verses": baid_verses,
        "reciter_folder": reciter,
        "estimated_minutes": max(5, estimated_minutes),
    }


# ── Exercise Processing ──────────────────────────────────────────

def process_exercise_answer(
    db: Session,
    student_id: uuid.UUID,
    surah_number: int,
    verse_number: int,
    exercise_type_str: str,
    is_correct: bool,
    wird_session_id: uuid.UUID | None = None,
    response_time_ms: int | None = None,
    attempt_number: int = 1,
    metadata: dict | None = None,
) -> dict:
    """
    Process an exercise answer: update mastery, SRS tier, XP.

    Returns dict with before/after scores, XP earned, etc.
    """
    # Parse exercise type
    try:
        exercise_type = ExerciseType(exercise_type_str)
    except ValueError:
        exercise_type = ExerciseType.PUZZLE  # Fallback

    # Get or create verse progress
    verse_prog = (
        db.query(VerseProgress)
        .filter(
            VerseProgress.student_id == student_id,
            VerseProgress.surah_number == surah_number,
            VerseProgress.verse_number == verse_number,
        )
        .first()
    )

    if not verse_prog:
        verse_prog = VerseProgress(
            student_id=student_id,
            surah_number=surah_number,
            verse_number=verse_number,
            mastery_score=0,
            mastery=VerseMastery.RED,
            next_review_date=date.today(),
        )
        db.add(verse_prog)
        db.flush()

    score_before = verse_prog.mastery_score
    tier_before = tier_from_score(score_before)

    # Calculate score delta
    delta = get_score_delta(exercise_type, is_correct)
    new_score = max(0, min(100, score_before + delta))

    # Special rule: if verse is ANCRE (tier 7) and fails, drop to ACQUIS (tier 4)
    tier_after = tier_from_score(new_score)
    if tier_before == SrsTier.ANCRE and not is_correct:
        new_score = max(new_score, 55)  # At least ACQUIS
        tier_after = tier_from_score(new_score)

    # Update verse progress
    verse_prog.mastery_score = new_score
    verse_prog.mastery = VerseMastery(update_mastery_from_score(new_score))
    verse_prog.review_count += 1
    verse_prog.next_review_date = calculate_next_review_date(tier_after)
    verse_prog.last_practiced_at = datetime.now(timezone.utc)

    if is_correct:
        verse_prog.consecutive_successes += 1
    else:
        verse_prog.consecutive_successes = 0

    # Log the exercise
    exercise_log = VerseExercise(
        student_id=student_id,
        wird_session_id=wird_session_id,
        surah_number=surah_number,
        verse_number=verse_number,
        exercise_type=exercise_type,
        is_correct=is_correct,
        response_time_ms=response_time_ms,
        attempt_number=attempt_number,
        metadata_json=metadata,
    )
    db.add(exercise_log)

    # Update Wird session stats if applicable
    if wird_session_id:
        wird = db.query(WirdSession).filter(WirdSession.id == wird_session_id).first()
        if wird:
            wird.total_exercises += 1
            if is_correct:
                wird.correct_exercises += 1

    # Calculate XP
    xp = XP_PER_EXERCISE_CORRECT if is_correct else XP_PER_EXERCISE_WRONG
    if tier_after.value > tier_before.value:
        xp += XP_BONUS_TIER_UP

    # Award XP to student
    _award_xp(db, student_id, xp)

    db.flush()

    stars = calculate_stars(new_score)

    return {
        "id": exercise_log.id,
        "mastery_score_before": score_before,
        "mastery_score_after": new_score,
        "srs_tier_before": tier_before.value,
        "srs_tier_after": tier_after.value,
        "xp_earned": xp,
        "next_review_date": verse_prog.next_review_date,
        "stars": stars,
    }


def process_step_result(
    db: Session,
    student_id: uuid.UUID,
    surah_number: int,
    verse_number: int,
    step: str,
    score: int,
    duration_seconds: int,
    wird_session_id: uuid.UUID | None = None,
    metadata: dict | None = None,
) -> dict:
    """
    Process a full step result (NOUR, TIKRAR, TAMRIN, TASMI, NATIJA).

    The step score is blended into the verse mastery_score.
    """
    # Get or create verse progress
    verse_prog = (
        db.query(VerseProgress)
        .filter(
            VerseProgress.student_id == student_id,
            VerseProgress.surah_number == surah_number,
            VerseProgress.verse_number == verse_number,
        )
        .first()
    )

    if not verse_prog:
        verse_prog = VerseProgress(
            student_id=student_id,
            surah_number=surah_number,
            verse_number=verse_number,
            mastery_score=0,
            mastery=VerseMastery.RED,
            next_review_date=date.today(),
        )
        db.add(verse_prog)
        db.flush()

    # Blend step score into mastery (weighted average)
    step_weights = {
        "NOUR": 0.05,    # Listening = small contribution
        "TIKRAR": 0.25,  # Repetition = significant
        "TAMRIN": 0.35,  # Exercises = most weight
        "TASMI": 0.30,   # Recitation = important
        "NATIJA": 0.0,   # Result screen = no score change
    }
    weight = step_weights.get(step, 0.1)

    if weight > 0:
        # Blend: new_score = old * (1 - weight) + step_score * weight
        old_score = verse_prog.mastery_score
        new_score = int(old_score * (1 - weight) + score * weight)
        new_score = max(0, min(100, new_score))

        verse_prog.mastery_score = new_score
        verse_prog.mastery = VerseMastery(update_mastery_from_score(new_score))

        tier = tier_from_score(new_score)
        verse_prog.next_review_date = calculate_next_review_date(tier)
        verse_prog.last_practiced_at = datetime.now(timezone.utc)
        verse_prog.total_practice_seconds += duration_seconds

    # XP for step completion
    step_xp = {"NOUR": 5, "TIKRAR": 15, "TAMRIN": 20, "TASMI": 15, "NATIJA": 5}
    xp = step_xp.get(step, 5)
    _award_xp(db, student_id, xp)

    db.flush()

    current_score = verse_prog.mastery_score
    tier = tier_from_score(current_score)
    stars = calculate_stars(current_score)

    return {
        "mastery_score": current_score,
        "srs_tier": tier.value,
        "stars": stars,
        "xp_earned": xp,
        "next_review_date": verse_prog.next_review_date,
    }


# ── Wird Session Management ──────────────────────────────────────

def start_wird(
    db: Session,
    student_id: uuid.UUID,
    surah_number: int | None = None,
) -> WirdSession:
    """Create or resume today's Wird session."""
    today = date.today()

    # Check for existing session today
    existing = (
        db.query(WirdSession)
        .filter(
            WirdSession.student_id == student_id,
            WirdSession.date == today,
        )
        .first()
    )

    if existing:
        return existing

    # Compose the Wird (with optional surah selection from Ikhtiar)
    composition = compose_wird(db, student_id, surah_number=surah_number)

    wird = WirdSession(
        student_id=student_id,
        date=today,
        status=WirdStatus.IN_PROGRESS,
        new_verses_count=len(composition["jadid_verses"]),
        qarib_count=len(composition["qarib_verses"]),
        baid_count=len(composition["baid_verses"]),
    )
    db.add(wird)
    db.flush()

    return wird


def complete_wird(
    db: Session,
    student_id: uuid.UUID,
    wird_id: uuid.UUID,
    duration_seconds: int,
    total_exercises: int,
    correct_exercises: int,
) -> WirdSession:
    """Mark a Wird session as completed."""
    wird = (
        db.query(WirdSession)
        .filter(
            WirdSession.id == wird_id,
            WirdSession.student_id == student_id,
        )
        .first()
    )
    if not wird:
        raise ValueError("Wird session not found")

    wird.status = WirdStatus.COMPLETED
    wird.completed_at = datetime.now(timezone.utc)
    wird.duration_seconds = duration_seconds
    wird.total_exercises = total_exercises
    wird.correct_exercises = correct_exercises

    # Award completion XP
    wird.xp_earned = XP_WIRD_COMPLETION
    _award_xp(db, student_id, XP_WIRD_COMPLETION)

    db.flush()
    return wird


# ── Journey Map ──────────────────────────────────────────────────

def build_journey_map(db: Session, student_id: uuid.UUID) -> dict:
    """Build the journey map with all surah progress."""
    from ..models.hifz_master import HifzGoal

    # Import surah data
    from ..routers.hifz_master import SURAH_VERSE_COUNTS

    # Surah names (just Juz Amma for now, 78-114)
    SURAH_NAMES = {
        78: ("النبأ", "An-Naba"),
        79: ("النازعات", "An-Naziat"),
        80: ("عبس", "Abasa"),
        81: ("التكوير", "At-Takwir"),
        82: ("الانفطار", "Al-Infitar"),
        83: ("المطففين", "Al-Mutaffifin"),
        84: ("الانشقاق", "Al-Inshiqaq"),
        85: ("البروج", "Al-Buruj"),
        86: ("الطارق", "At-Tariq"),
        87: ("الأعلى", "Al-Ala"),
        88: ("الغاشية", "Al-Ghashiya"),
        89: ("الفجر", "Al-Fajr"),
        90: ("البلد", "Al-Balad"),
        91: ("الشمس", "Ash-Shams"),
        92: ("الليل", "Al-Layl"),
        93: ("الضحى", "Ad-Duha"),
        94: ("الشرح", "Ash-Sharh"),
        95: ("التين", "At-Tin"),
        96: ("العلق", "Al-Alaq"),
        97: ("القدر", "Al-Qadr"),
        98: ("البينة", "Al-Bayyina"),
        99: ("الزلزلة", "Az-Zalzala"),
        100: ("العاديات", "Al-Adiyat"),
        101: ("القارعة", "Al-Qaria"),
        102: ("التكاثر", "At-Takathur"),
        103: ("العصر", "Al-Asr"),
        104: ("الهمزة", "Al-Humaza"),
        105: ("الفيل", "Al-Fil"),
        106: ("قريش", "Quraysh"),
        107: ("الماعون", "Al-Maun"),
        108: ("الكوثر", "Al-Kawthar"),
        109: ("الكافرون", "Al-Kafirun"),
        110: ("النصر", "An-Nasr"),
        111: ("المسد", "Al-Masad"),
        112: ("الإخلاص", "Al-Ikhlas"),
        113: ("الفلق", "Al-Falaq"),
        114: ("الناس", "An-Nas"),
    }

    # Get all verse progress for student
    all_progress = (
        db.query(
            VerseProgress.surah_number,
            func.count(VerseProgress.id).label("started"),
            func.count(
                func.nullif(VerseProgress.mastery_score < 70, True)
            ).label("mastered"),
            func.avg(VerseProgress.mastery_score).label("avg_score"),
        )
        .filter(VerseProgress.student_id == student_id)
        .group_by(VerseProgress.surah_number)
        .all()
    )
    progress_map = {
        r.surah_number: {
            "started": r.started,
            "mastered": r.mastered,
            "avg_score": float(r.avg_score or 0),
        }
        for r in all_progress
    }

    # Get goals
    goals = (
        db.query(HifzGoal.surah_number)
        .filter(HifzGoal.student_id == student_id)
        .all()
    )
    goal_surahs = {g.surah_number for g in goals}

    # Build map entries (Juz Amma: 78-114)
    surahs = []
    total_stars = 0
    total_memorized = 0

    for sn in range(78, 115):
        total_v = SURAH_VERSE_COUNTS[sn - 1]
        prog = progress_map.get(sn, {"started": 0, "mastered": 0, "avg_score": 0})
        max_stars = total_v * 3
        # Approximate stars from average score
        approx_stars = int(prog["started"] * calculate_stars(int(prog["avg_score"])))

        entry = {
            "surah_number": sn,
            "name_ar": SURAH_NAMES.get(sn, ("", ""))[0],
            "name_fr": SURAH_NAMES.get(sn, ("", ""))[1],
            "total_verses": total_v,
            "verses_started": prog["started"],
            "verses_mastered": prog["mastered"],
            "total_stars": approx_stars,
            "max_stars": max_stars,
            "average_score": prog["avg_score"],
            "is_completed": prog["mastered"] >= total_v and total_v > 0,
            "has_goal": sn in goal_surahs,
        }
        surahs.append(entry)
        total_stars += approx_stars
        total_memorized += prog["mastered"]

    # Get student XP
    xp_record = db.query(StudentXP).filter(StudentXP.student_id == student_id).first()
    total_xp = xp_record.total_xp if xp_record else 0
    level = xp_record.level.value if xp_record else "DEBUTANT"
    title = get_title(total_xp)

    return {
        "surahs": surahs,
        "total_verses_memorized": total_memorized,
        "total_stars": total_stars,
        "current_streak": 0,  # TODO: calculate from wird_sessions
        "total_xp": total_xp,
        "level": level,
        "title_ar": title["ar"],
        "title_fr": title["fr"],
    }


# ── Checkpoint Processing (Phase 2) ─────────────────────────────

def process_checkpoint(
    db: Session,
    student_id: uuid.UUID,
    surah_number: int,
    verse_start: int,
    verse_end: int,
    tartib_score: int,
    takamul_score: int,
    tasmi_score: int,
    verse_scores: list[dict] | None = None,
    duration_seconds: int = 0,
    wird_session_id: uuid.UUID | None = None,
) -> dict:
    """
    Process a checkpoint result: update SRS for all verses in the group.

    The checkpoint global score is a weighted average of the 3 exercise scores.
    Each verse in the range gets its mastery_score blended with the checkpoint score.
    """
    # Weighted average for checkpoint global score
    global_score = int(tartib_score * 0.25 + takamul_score * 0.35 + tasmi_score * 0.40)
    global_score = max(0, min(100, global_score))

    stars = calculate_stars(global_score)
    total_xp = 0
    verses_updated = 0

    # Build per-verse score map (if provided, use it; otherwise use global)
    verse_score_map = {}
    if verse_scores:
        for vs in verse_scores:
            verse_score_map[(vs["surah_number"], vs["verse_number"])] = vs["score"]

    # Update each verse in the range
    for v_num in range(verse_start, verse_end + 1):
        verse_prog = (
            db.query(VerseProgress)
            .filter(
                VerseProgress.student_id == student_id,
                VerseProgress.surah_number == surah_number,
                VerseProgress.verse_number == v_num,
            )
            .first()
        )

        if not verse_prog:
            verse_prog = VerseProgress(
                student_id=student_id,
                surah_number=surah_number,
                verse_number=v_num,
                mastery_score=0,
                mastery=VerseMastery.RED,
                next_review_date=date.today(),
            )
            db.add(verse_prog)
            db.flush()

        # Use per-verse score if available, otherwise global checkpoint score
        checkpoint_score = verse_score_map.get((surah_number, v_num), global_score)

        # Blend checkpoint score into mastery (weight = 0.30 for checkpoint)
        old_score = verse_prog.mastery_score
        new_score = int(old_score * 0.70 + checkpoint_score * 0.30)
        new_score = max(0, min(100, new_score))

        verse_prog.mastery_score = new_score
        verse_prog.mastery = VerseMastery(update_mastery_from_score(new_score))
        verse_prog.review_count += 1
        verse_prog.last_practiced_at = datetime.now(timezone.utc)
        verse_prog.total_practice_seconds += duration_seconds // max(1, verse_end - verse_start + 1)

        tier = tier_from_score(new_score)
        verse_prog.next_review_date = calculate_next_review_date(tier)

        verses_updated += 1

    # XP: base checkpoint XP + bonus for good score
    checkpoint_xp = 25  # Base XP for completing a checkpoint
    if global_score >= 90:
        checkpoint_xp += 20  # Bonus for excellence
    elif global_score >= 70:
        checkpoint_xp += 10  # Bonus for good performance
    total_xp = checkpoint_xp

    _award_xp(db, student_id, total_xp)

    # Update Wird session stats if applicable
    if wird_session_id:
        wird = db.query(WirdSession).filter(WirdSession.id == wird_session_id).first()
        if wird:
            wird.total_exercises += 3  # 3 checkpoint exercises
            wird.xp_earned += total_xp

    db.flush()

    return {
        "global_score": global_score,
        "stars": stars,
        "xp_earned": total_xp,
        "verses_updated": verses_updated,
        "scores_by_step": {
            "tartib": tartib_score,
            "takamul": takamul_score,
            "tasmi": tasmi_score,
        },
    }


# ── Suggested Surahs (Ikhtiar Screen) ───────────────────────────

def get_suggested_surahs(db: Session, student_id: uuid.UUID) -> dict:
    """
    Build suggested surahs for the Ikhtiar (selection) screen.

    Returns:
      - current_surah: the surah currently in progress (from active goal)
      - suggestions: up to 3 surahs to start next
      - review_due_surahs: surahs with verses needing review
    """
    from ..models.quran import Surah
    from ..routers.hifz_master import SURAH_VERSE_COUNTS

    # ── SURAH_NAMES for Juz Amma ──
    SURAH_NAMES = {
        78: ("النبأ", "An-Naba"), 79: ("النازعات", "An-Naziat"),
        80: ("عبس", "Abasa"), 81: ("التكوير", "At-Takwir"),
        82: ("الانفطار", "Al-Infitar"), 83: ("المطففين", "Al-Mutaffifin"),
        84: ("الانشقاق", "Al-Inshiqaq"), 85: ("البروج", "Al-Buruj"),
        86: ("الطارق", "At-Tariq"), 87: ("الأعلى", "Al-Ala"),
        88: ("الغاشية", "Al-Ghashiya"), 89: ("الفجر", "Al-Fajr"),
        90: ("البلد", "Al-Balad"), 91: ("الشمس", "Ash-Shams"),
        92: ("الليل", "Al-Layl"), 93: ("الضحى", "Ad-Duha"),
        94: ("الشرح", "Ash-Sharh"), 95: ("التين", "At-Tin"),
        96: ("العلق", "Al-Alaq"), 97: ("القدر", "Al-Qadr"),
        98: ("البينة", "Al-Bayyina"), 99: ("الزلزلة", "Az-Zalzala"),
        100: ("العاديات", "Al-Adiyat"), 101: ("القارعة", "Al-Qaria"),
        102: ("التكاثر", "At-Takathur"), 103: ("العصر", "Al-Asr"),
        104: ("الهمزة", "Al-Humaza"), 105: ("الفيل", "Al-Fil"),
        106: ("قريش", "Quraysh"), 107: ("الماعون", "Al-Maun"),
        108: ("الكوثر", "Al-Kawthar"), 109: ("الكافرون", "Al-Kafirun"),
        110: ("النصر", "An-Nasr"), 111: ("المسد", "Al-Masad"),
        112: ("الإخلاص", "Al-Ikhlas"), 113: ("الفلق", "Al-Falaq"),
        114: ("الناس", "An-Nas"),
    }

    today = date.today()

    # Get active goal
    goal = (
        db.query(HifzGoal)
        .filter(
            HifzGoal.student_id == student_id,
            HifzGoal.is_completed == False,
        )
        .order_by(HifzGoal.started_at.desc())
        .first()
    )

    # Get all verse progress grouped by surah
    all_progress = (
        db.query(
            VerseProgress.surah_number,
            func.count(VerseProgress.id).label("started"),
            func.max(VerseProgress.verse_number).label("last_verse"),
            func.avg(VerseProgress.mastery_score).label("avg_score"),
        )
        .filter(VerseProgress.student_id == student_id)
        .group_by(VerseProgress.surah_number)
        .all()
    )
    progress_map = {
        r.surah_number: {
            "started": r.started,
            "last_verse": r.last_verse,
            "avg_score": float(r.avg_score or 0),
        }
        for r in all_progress
    }

    # Count review-due verses per surah
    review_due_rows = (
        db.query(
            VerseProgress.surah_number,
            func.count(VerseProgress.id).label("due_count"),
        )
        .filter(
            VerseProgress.student_id == student_id,
            VerseProgress.next_review_date <= today + timedelta(days=1),
        )
        .group_by(VerseProgress.surah_number)
        .all()
    )
    review_due_map = {r.surah_number: r.due_count for r in review_due_rows}

    def _build_entry(sn: int, reason: str) -> dict:
        names = SURAH_NAMES.get(sn, ("", ""))
        total_v = SURAH_VERSE_COUNTS[sn - 1] if sn <= len(SURAH_VERSE_COUNTS) else 0
        prog = progress_map.get(sn, {"started": 0, "last_verse": 0, "avg_score": 0})
        next_v = (prog["last_verse"] or 0) + 1
        return {
            "surah_number": sn,
            "name_ar": names[0],
            "name_fr": names[1],
            "total_verses": total_v,
            "verses_started": prog["started"],
            "verses_remaining": max(0, total_v - prog["started"]),
            "next_verse": min(next_v, total_v),
            "average_score": round(prog["avg_score"], 1),
            "has_review_due": sn in review_due_map,
            "review_count": review_due_map.get(sn, 0),
            "reason": reason,
        }

    # ── Current surah (from active goal) ──
    current_surah = None
    if goal:
        prog = progress_map.get(goal.surah_number, {"started": 0, "last_verse": 0})
        if (prog["last_verse"] or 0) < goal.total_verses:
            current_surah = _build_entry(goal.surah_number, "in_progress")

    # ── Suggestions: surahs not yet started, starting from shortest ──
    suggestions = []
    # Start from An-Nas (114) going down — shorter surahs first
    for sn in range(114, 77, -1):
        if sn in progress_map:
            continue  # Already started
        if current_surah and sn == current_surah["surah_number"]:
            continue
        suggestions.append(_build_entry(sn, "suggested"))
        if len(suggestions) >= 3:
            break

    # ── Review due surahs ──
    review_due_surahs = []
    for sn, count in sorted(review_due_map.items(), key=lambda x: -x[1]):
        if current_surah and sn == current_surah["surah_number"]:
            continue
        review_due_surahs.append(_build_entry(sn, "review_due"))
        if len(review_due_surahs) >= 5:
            break

    return {
        "current_surah": current_surah,
        "suggestions": suggestions,
        "review_due_surahs": review_due_surahs,
    }


# ── Private Helpers ──────────────────────────────────────────────

def _award_xp(db: Session, student_id: uuid.UUID, xp_amount: int) -> None:
    """Award XP to student, create StudentXP if needed."""
    xp_record = db.query(StudentXP).filter(StudentXP.student_id == student_id).first()

    if not xp_record:
        xp_record = StudentXP(student_id=student_id, total_xp=0)
        db.add(xp_record)
        db.flush()

    xp_record.total_xp += xp_amount

    # Update level
    if xp_record.total_xp >= 10000:
        xp_record.level = StudentLevel.HAFIZ_EXPERT
    elif xp_record.total_xp >= 5000:
        xp_record.level = StudentLevel.HAFIZ_CONFIRME
    elif xp_record.total_xp >= 2000:
        xp_record.level = StudentLevel.HAFIZ_EN_HERBE
    elif xp_record.total_xp >= 500:
        xp_record.level = StudentLevel.APPRENTI
    else:
        xp_record.level = StudentLevel.DEBUTANT

    xp_record.updated_at = datetime.now(timezone.utc)
