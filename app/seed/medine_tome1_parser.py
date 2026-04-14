"""
Parser for the optimized Tome 1 Médine Markdown file.

Extracts structured JSON blocks:
  - Quiz questions (Parts 1-7 + Final Exam)
  - Flashcard cards (Parts 1-7 + Synthesis)
  - Adaptive Diagnostic Test v2.0

These JSON blocks are embedded as ```json fenced code blocks in the MD file.
The parser identifies them by their surrounding section headers.

Usage:
    from .medine_tome1_parser import parse_tome1_md
    data = parse_tome1_md("/path/to/Tome1.md")
"""
import json
import re
from pathlib import Path
from typing import Any


def _extract_json_blocks(md_text: str) -> list[dict[str, Any]]:
    """Extract all ```json ... ``` fenced code blocks from markdown text."""
    pattern = r"```json\s*\n(.*?)```"
    matches = re.findall(pattern, md_text, re.DOTALL)
    blocks = []
    for match in matches:
        try:
            blocks.append(json.loads(match.strip()))
        except json.JSONDecodeError as e:
            print(f"⚠ JSON parse error (skipping block): {e}")
            continue
    return blocks


def _classify_block(block: dict[str, Any], header_context: str) -> tuple[str, Any]:
    """Classify a JSON block by its content and surrounding header."""
    # Quiz blocks — two formats:
    #   Format A (Parts 1-2): {"quizzes": [{lesson, title, questions: [{id, question, options, correct}]}]}
    #   Format B (Parts 3-7): {"quizTitle": "...", "questions": [{id, question, options, correctIndex}]}
    if "quizzes" in block:
        return "quiz", block
    if "quizTitle" in block and "questions" in block:
        return "quiz_alt", block
    # Flashcard blocks — two formats:
    #   Format A (Parts 1-2): {"flashcards": [{lesson, title, cards: [{id, front, back, ...}]}]}
    #   Format B (Parts 3-7): {"flashcard_set": "...", "cards": [{front, back, category}]}
    if "flashcards" in block:
        return "flashcard", block
    if "flashcard_set" in block and "cards" in block:
        return "flashcard_alt", block
    # Diagnostic block has "testName" or "diagnosticLogic"
    if "testName" in block or "diagnosticLogic" in block:
        return "diagnostic", block
    # Final exam block has "examTitle"
    if "examTitle" in block:
        return "exam", block
    return "unknown", block


def _normalize_quiz_alt(block: dict, header: str) -> dict:
    """
    Normalize alt quiz format (Parts 3-7) to standard format.
    Alt: {"quizTitle": ..., "questions": [{id, question, options, correctIndex}]}
    Standard: {"quizzes": [{lesson, title, questions: [{id, question, options, correct}]}]}
    """
    title = block.get("quizTitle", "")
    # Try to extract lesson range from title or header context
    # (e.g., "Leçons 9-11" or "Leçons 12–15")
    lesson_match = re.search(r"[Ll]eçons?\s+(\d+)", title)
    if not lesson_match:
        lesson_match = re.search(r"[Ll]eçons?\s+(\d+)", header)
    lesson_start = int(lesson_match.group(1)) if lesson_match else 0

    normalized_questions = []
    for q in block.get("questions", []):
        normalized_questions.append({
            "id": f"L{lesson_start}Q{q.get('id', 0)}",
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct": q.get("correctIndex", q.get("correct", 0)),
            "explanation": q.get("explanation", ""),
        })

    return {
        "quizzes": [{
            "lesson": lesson_start,
            "title": title,
            "questions": normalized_questions,
        }]
    }


def _normalize_flashcard_alt(block: dict, header: str, part_number: int = 0) -> dict:
    """
    Normalize alt flashcard format (Parts 3-7) to standard format.
    Alt: {"flashcard_set": ..., "cards": [{front, back, category}]}
    Standard: {"flashcards": [{lesson, title, cards: [{id, front, back, ...}]}]}
    """
    title = block.get("flashcard_set", "")
    lesson_match = re.search(r"[Ll]eçons?\s+(\d+)", title)
    if not lesson_match:
        lesson_match = re.search(r"[Ll]eçons?\s+(\d+)", header)
    lesson_start = int(lesson_match.group(1)) if lesson_match else 0

    normalized_cards = []
    for i, card in enumerate(block.get("cards", []), 1):
        normalized_cards.append({
            "id": f"P{part_number}F{lesson_start}C{i}",
            "front": card.get("front", ""),
            "back": card.get("back", ""),
            "arabicExample": card.get("arabicExample", ""),
            "englishExample": card.get("englishExample", ""),
            "category": card.get("category", ""),
        })

    return {
        "flashcards": [{
            "lesson": lesson_start,
            "title": title,
            "cards": normalized_cards,
        }]
    }


def _normalize_exam(block: dict) -> dict:
    """Normalize final exam format to standard quiz format."""
    normalized_questions = []
    for q in block.get("questions", []):
        normalized_questions.append({
            "id": f"EXAM_Q{q.get('id', 0)}",
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct": q.get("correctIndex", q.get("correct", 0)),
            "explanation": q.get("explanation", ""),
        })

    return {
        "quizzes": [{
            "lesson": 0,  # covers all lessons
            "title": block.get("examTitle", "Examen Final"),
            "questions": normalized_questions,
        }]
    }


def _extract_blocks_with_context(md_text: str) -> list[tuple[str, dict]]:
    """Extract JSON blocks with their preceding header context."""
    results = []
    # Find each ```json block and its preceding ## header
    json_pattern = r"```json\s*\n(.*?)```"
    header_pattern = r"^##\s+(.+)$"

    lines = md_text.split("\n")
    in_json = False
    json_buffer = []
    last_header = ""

    for line in lines:
        # Track the most recent ## header
        header_match = re.match(header_pattern, line)
        if header_match:
            last_header = header_match.group(1).strip()

        # Strip zero-width spaces and other invisible chars before comparing
        clean_line = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', line).strip()
        if clean_line == "```json":
            in_json = True
            json_buffer = []
            continue
        elif in_json and clean_line == "```":
            in_json = False
            raw = "\n".join(json_buffer)
            try:
                block = json.loads(raw)
                block_type, data = _classify_block(block, last_header)
                results.append((block_type, data, last_header))
            except json.JSONDecodeError as e:
                print(f"⚠ JSON error near '{last_header}': {e}")
            continue

        if in_json:
            json_buffer.append(line)

    return results


def parse_tome1_md(md_path: str) -> dict[str, Any]:
    """
    Parse the optimized Tome 1 Médine markdown file.

    Returns:
        {
            "quizzes": {
                "part1": {"quizzes": [...]},
                "part2": {...},
                ...
            },
            "flashcards": {
                "part1": {"flashcards": [...]},
                ...
            },
            "diagnostic": {...},
            "exam": {...},
        }
    """
    md_text = Path(md_path).read_text(encoding="utf-8")
    blocks = _extract_blocks_with_context(md_text)

    result = {
        "quizzes": {},
        "flashcards": {},
        "diagnostic": None,
        "exam": None,
    }

    quiz_counter = 0
    flashcard_counter = 0

    for block_type, data, header in blocks:
        if block_type == "quiz":
            quiz_counter += 1
            key = f"part{quiz_counter}"
            result["quizzes"][key] = data
        elif block_type == "quiz_alt":
            # Normalize alt format to standard format
            quiz_counter += 1
            key = f"part{quiz_counter}"
            result["quizzes"][key] = _normalize_quiz_alt(data, header)
        elif block_type == "flashcard":
            flashcard_counter += 1
            key = f"part{flashcard_counter}"
            result["flashcards"][key] = data
        elif block_type == "flashcard_alt":
            flashcard_counter += 1
            key = f"part{flashcard_counter}"
            result["flashcards"][key] = _normalize_flashcard_alt(data, header, part_number=flashcard_counter)
        elif block_type == "diagnostic":
            result["diagnostic"] = data
        elif block_type == "exam":
            # Treat final exam as an additional quiz part
            quiz_counter += 1
            key = f"part{quiz_counter}"
            result["quizzes"][key] = _normalize_exam(data)
            result["exam"] = data

    print(f"✓ Parsed {quiz_counter} quiz blocks, {flashcard_counter} flashcard blocks")
    if result["diagnostic"]:
        q_count = len(result["diagnostic"].get("questions", []))
        print(f"✓ Parsed diagnostic test with {q_count} questions")
    if result["exam"]:
        print(f"✓ Parsed final exam")

    return result


# ── Helpers: flatten quiz questions ──────────────────────────────────────────

def flatten_quiz_questions(parsed: dict) -> list[dict[str, Any]]:
    """
    Flatten all quiz questions from all parts into a single list.
    Each question gets lesson_number, part_number, and a sequential id.
    """
    all_questions = []
    for part_key, part_data in sorted(parsed["quizzes"].items()):
        part_num = int(part_key.replace("part", ""))
        for quiz in part_data.get("quizzes", []):
            lesson_num = quiz.get("lesson", 0)
            for q in quiz.get("questions", []):
                all_questions.append({
                    "id_str": q.get("id", ""),
                    "lesson_number": lesson_num,
                    "part_number": part_num,
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "correct": q.get("correct", 0),
                    "explanation": q.get("explanation", ""),
                })
    return all_questions


def flatten_flashcard_cards(parsed: dict) -> list[dict[str, Any]]:
    """
    Flatten all flashcard cards from all parts into a single list.
    """
    all_cards = []
    for part_key, part_data in sorted(parsed["flashcards"].items()):
        part_num = int(part_key.replace("part", ""))
        for fc_group in part_data.get("flashcards", []):
            lesson_num = fc_group.get("lesson", 0)
            for card in fc_group.get("cards", []):
                all_cards.append({
                    "card_id_str": card.get("id", ""),
                    "lesson_number": lesson_num,
                    "part_number": part_num,
                    "front_ar": card.get("front", ""),
                    "back_fr": card.get("back", ""),
                    "arabic_example": card.get("arabicExample", ""),
                    "french_example": card.get("englishExample", ""),
                })
    return all_cards


def flatten_diagnostic_questions(parsed: dict) -> list[dict[str, Any]]:
    """
    Flatten diagnostic questions and assign pool (A/B/C) based on difficulty.
    """
    diag = parsed.get("diagnostic")
    if not diag:
        return []

    questions = diag.get("questions", [])
    pool_map = {1: "A", 2: "B", 3: "C"}
    result = []
    for q in questions:
        difficulty = q.get("difficulty", 1)
        result.append({
            "id_str": q.get("id", ""),
            "pool": pool_map.get(difficulty, "A"),
            "difficulty": difficulty,
            "skill_tested": q.get("skillTested", ""),
            "lesson_ref": q.get("leçon_cible", q.get("lecon_cible", "")),
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct": q.get("correct", 0),
            "explanation": q.get("explanation", ""),
            "adaptive_hint": q.get("adaptiveHint", ""),
        })
    return result


# ── CLI usage ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    md_path = sys.argv[1] if len(sys.argv) > 1 else "📚 Tome 1 Médine — Édition Optimisée.md"
    data = parse_tome1_md(md_path)
    print(f"\nQuiz parts: {list(data['quizzes'].keys())}")
    print(f"Flashcard parts: {list(data['flashcards'].keys())}")

    questions = flatten_quiz_questions(data)
    print(f"Total quiz questions: {len(questions)}")

    cards = flatten_flashcard_cards(data)
    print(f"Total flashcard cards: {len(cards)}")

    diag_qs = flatten_diagnostic_questions(data)
    print(f"Diagnostic questions: {len(diag_qs)}")
