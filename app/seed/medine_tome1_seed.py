"""
Seed data for the full Medine Tome 1 content from the optimized Markdown.

Seeds:
  - FlashcardCards (193 cards from 8 parts)
  - DiagnosticQuestions (10 adaptive questions with pools A/B/C)
  - Badges (8 gamification badges from specs)

Relies on:
  - medine_tome1_parser.py to extract structured data from the MD file
  - New models: FlashcardCard, DiagnosticQuestion, Badge (from migration 006)

Run: called from main.py lifespan (idempotent)
"""
import os
from pathlib import Path
from datetime import datetime

from ..database import SessionLocal
from ..models.flashcard import FlashcardCard
from ..models.diagnostic import DiagnosticQuestion
from ..models.gamification import Badge
from .medine_tome1_parser import (
    parse_tome1_md,
    flatten_flashcard_cards,
    flatten_diagnostic_questions,
)


# ── Path to the optimized MD file ────────────────────────────────────────────
# Located in backend/data/ (copied there for Docker compatibility)
_MD_FILENAME = "📚 Tome 1 Médine — Édition Optimisée.md"
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
_MD_PATH = _BACKEND_DIR / "data" / _MD_FILENAME


# ── Badge Catalogue (from TALEEM_Specifications_Techniques.docx) ─────────────

BADGE_CATALOGUE = [
    {
        "code": "premier_pas",
        "name_fr": "Premier Pas",
        "description_fr": "Terminer la leçon 1",
        "icon": "footprints",
        "condition_type": "lesson_complete",
        "condition_value": {"lesson_number": 1},
        "sort_order": 1,
    },
    {
        "code": "detective",
        "name_fr": "Détective",
        "description_fr": "100% au quiz de la Partie 1",
        "icon": "search",
        "condition_type": "quiz_perfect",
        "condition_value": {"part_number": 1},
        "sort_order": 2,
    },
    {
        "code": "maitre_idafa",
        "name_fr": "Maître de l'Idafa",
        "description_fr": "3 étoiles sur les leçons 5-8",
        "icon": "library_books",
        "condition_type": "stars_range",
        "condition_value": {"lesson_start": 5, "lesson_end": 8, "min_stars": 3},
        "sort_order": 3,
    },
    {
        "code": "verbe_en_feu",
        "name_fr": "Verbe en Feu",
        "description_fr": "10 verbes conjugués sans erreur",
        "icon": "local_fire_department",
        "condition_type": "verbs_streak",
        "condition_value": {"count": 10},
        "sort_order": 4,
    },
    {
        "code": "marathonien",
        "name_fr": "Marathonien",
        "description_fr": "Streak de 30 jours consécutifs",
        "icon": "directions_run",
        "condition_type": "streak_days",
        "condition_value": {"days": 30},
        "sort_order": 5,
    },
    {
        "code": "savant_diptotes",
        "name_fr": "Savant des Diptotes",
        "description_fr": "100% au quiz Partie 6 (Nombres et Diptotes)",
        "icon": "star",
        "condition_type": "quiz_perfect",
        "condition_value": {"part_number": 6},
        "sort_order": 6,
    },
    {
        "code": "gardien_medine",
        "name_fr": "Gardien de Médine",
        "description_fr": "Examen final > 90%",
        "icon": "castle",
        "condition_type": "exam_score",
        "condition_value": {"min_percent": 90},
        "sort_order": 7,
    },
    {
        "code": "polyglotte",
        "name_fr": "Polyglotte",
        "description_fr": "200 flashcards maîtrisées (interval > 21 jours)",
        "icon": "psychology",
        "condition_type": "flashcards_mastered",
        "condition_value": {"count": 200, "min_interval_days": 21},
        "sort_order": 8,
    },
]


# ── Seed Functions ───────────────────────────────────────────────────────────

def _seed_flashcard_cards(db, parsed_data: dict) -> int:
    """Seed FlashcardCard table from parsed MD data. Returns count of new cards."""
    cards_data = flatten_flashcard_cards(parsed_data)
    count = 0

    for card_data in cards_data:
        card_id_str = card_data["card_id_str"]
        if not card_id_str:
            continue

        # Skip if already exists (idempotent)
        existing = db.query(FlashcardCard).filter_by(card_id_str=card_id_str).first()
        if existing:
            continue

        card = FlashcardCard(
            lesson_number=card_data["lesson_number"],
            part_number=card_data["part_number"],
            card_id_str=card_id_str,
            front_ar=card_data["front_ar"],
            back_fr=card_data["back_fr"],
            arabic_example=card_data.get("arabic_example") or None,
            french_example=card_data.get("french_example") or None,
            category=card_data.get("category") or None,
            sort_order=count + 1,
        )
        db.add(card)
        count += 1

    if count > 0:
        db.flush()
    return count


def _seed_diagnostic_questions(db, parsed_data: dict) -> int:
    """Seed DiagnosticQuestion table from parsed MD data. Returns count of new questions."""
    questions_data = flatten_diagnostic_questions(parsed_data)
    count = 0

    for i, q_data in enumerate(questions_data):
        # Check by question text (no unique id_str in diagnostic)
        existing = db.query(DiagnosticQuestion).filter_by(
            question=q_data["question"]
        ).first()
        if existing:
            continue

        question = DiagnosticQuestion(
            pool=q_data["pool"],
            difficulty=q_data["difficulty"],
            skill_tested=q_data["skill_tested"],
            lesson_ref=q_data.get("lesson_ref") or None,
            question=q_data["question"],
            options=q_data["options"],
            correct=q_data["correct"],
            explanation=q_data.get("explanation") or None,
            adaptive_hint=q_data.get("adaptive_hint") or None,
            sort_order=i + 1,
        )
        db.add(question)
        count += 1

    if count > 0:
        db.flush()
    return count


def _seed_badges(db) -> int:
    """Seed Badge table from the static catalogue. Returns count of new badges."""
    count = 0
    for badge_data in BADGE_CATALOGUE:
        existing = db.query(Badge).filter_by(code=badge_data["code"]).first()
        if existing:
            # Update in case description changed
            existing.name_fr = badge_data["name_fr"]
            existing.description_fr = badge_data["description_fr"]
            existing.icon = badge_data["icon"]
            existing.condition_type = badge_data["condition_type"]
            existing.condition_value = badge_data["condition_value"]
            existing.sort_order = badge_data["sort_order"]
            continue

        badge = Badge(
            code=badge_data["code"],
            name_fr=badge_data["name_fr"],
            description_fr=badge_data["description_fr"],
            icon=badge_data["icon"],
            condition_type=badge_data["condition_type"],
            condition_value=badge_data["condition_value"],
            sort_order=badge_data["sort_order"],
        )
        db.add(badge)
        count += 1

    if count > 0:
        db.flush()
    return count


def _seed_quiz_to_extra_data(db, parsed_data: dict) -> int:
    """
    Enrich existing CurriculumItem extra_data with quiz questions from the MD.
    The medine_enriched.py seed already creates CurriculumItems with quiz data
    from its own LESSON_X dicts, but the MD has more comprehensive quiz sets.
    This function merges the MD quiz data into the existing items.
    Returns count of updated items.
    """
    from ..models.curriculum import CurriculumItem, CurriculumUnit, CurriculumProgram, CurriculumType
    from .medine_tome1_parser import flatten_quiz_questions

    program = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.MEDINE_T1
    ).first()
    if not program:
        return 0

    all_questions = flatten_quiz_questions(parsed_data)
    # Group questions by lesson number
    by_lesson: dict[int, list] = {}
    for q in all_questions:
        lesson_num = q["lesson_number"]
        if lesson_num == 0:
            continue  # exam questions, skip for per-lesson enrichment
        by_lesson.setdefault(lesson_num, []).append(q)

    count = 0
    for lesson_num, questions in by_lesson.items():
        unit = db.query(CurriculumUnit).filter_by(
            curriculum_program_id=program.id,
            number=lesson_num
        ).first()
        if not unit:
            continue

        item = db.query(CurriculumItem).filter_by(
            curriculum_unit_id=unit.id,
            number=1,
        ).first()
        if not item:
            continue

        # Merge MD quiz questions into extra_data
        extra = dict(item.extra_data or {})
        md_quiz = [{
            "id": q["id_str"],
            "question": q["question"],
            "options": q["options"],
            "correct": q["correct"],
            "explanation": q.get("explanation", ""),
        } for q in questions]

        extra["quiz_md"] = md_quiz
        item.extra_data = extra
        count += 1

    if count > 0:
        db.flush()
    return count


# ── Main entry point ─────────────────────────────────────────────────────────

def seed_medine_tome1(db=None) -> None:
    """
    Seed all Medine Tome 1 content from the optimized Markdown file.
    Creates flashcard cards, diagnostic questions, and badges.
    Idempotent — safe to run multiple times.
    """
    if db is None:
        db = SessionLocal()

    # Check if MD file exists
    if not _MD_PATH.exists():
        print(f"⚠ MD file not found at {_MD_PATH}, skipping Tome 1 seed")
        return

    # Parse the MD file
    try:
        parsed = parse_tome1_md(str(_MD_PATH))
    except Exception as e:
        print(f"⚠ Failed to parse MD file: {e}")
        return

    # Seed each component
    badge_count = _seed_badges(db)
    card_count = _seed_flashcard_cards(db, parsed)
    diag_count = _seed_diagnostic_questions(db, parsed)
    quiz_count = _seed_quiz_to_extra_data(db, parsed)

    db.commit()

    print(f"✓ Seeded Tome 1 content:")
    print(f"  • {badge_count} new badges (8 total)")
    print(f"  • {card_count} new flashcard cards (193 total)")
    print(f"  • {diag_count} new diagnostic questions (10 total)")
    print(f"  • {quiz_count} lessons enriched with MD quiz data")


if __name__ == "__main__":
    seed_medine_tome1()
