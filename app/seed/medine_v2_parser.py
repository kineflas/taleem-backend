"""
Tome 1 Médine — V2 Parser
Reads the optimised MD file and produces lessons_content_v2.json
with structured discovery_cards, exercises, dialogue, quiz & flashcards.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

MD_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "📚 Tome 1 Médine — Édition Optimisée.md"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "lessons_content_v2.json"

LESSON_TO_PART: dict[int, int] = {
    1: 1, 2: 1, 3: 1, 4: 1,
    5: 2, 6: 2, 7: 2, 8: 2,
    9: 3, 10: 3, 11: 3,
    12: 4, 13: 4, 14: 4, 15: 4,
    16: 5, 17: 5, 18: 5,
    19: 6, 20: 6, 21: 6,
    22: 7, 23: 7,
}

PART_NAMES: dict[int, str] = {
    1: "Les bases de la désignation et de la phrase simple",
    2: "Genre, Possession et Distance",
    3: "Qualification et Pronoms personnels",
    4: "L'entrée dans l'Action (Le Verbe au Passé)",
    5: "Règles avancées et Pluriels d'objets",
    6: "Mathématiques et Structures complexes",
    7: "Le Temps Présent",
}

# ── Regex patterns ─────────────────────────────────────────────────────────
RE_LESSON = re.compile(
    r'^#{1,2}\s+(?:\S+\s+)?[Ll][Ee][Çç][Oo][Nn]\s+(\d+)\s*[:\-—]\s*(.+)',
    re.MULTILINE,
)
RE_OBJECTIVE = re.compile(r'>\s*\*\*Objectif\s*:?\*\*\s*:?\s*(.+)', re.IGNORECASE)
RE_SECTION_HEADER = re.compile(r'^#{2,3}\s+(?:\*\*)?(?:\d+[\.\)]\s*)?(.+?)(?:\*\*)?$', re.MULTILINE)
RE_DIALOGUE_LINE = re.compile(r'\*\*(.+?)\s*:?\*\*\s*:?\s*(.+)')
RE_AUDIO_LINE = re.compile(r'🔊\s*\[Audio\s*:\s*prononciation de\s*[""«](.+?)[""»]\s*[-—]\s*(.+?)\]', re.IGNORECASE)
RE_TABLE_ROW = re.compile(r'^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', re.MULTILINE)
RE_JSON_BLOCK = re.compile(r'```json\s*([\s\S]*?)\s*```')
RE_FILL_BLANK_ITEM = re.compile(r'[-•]\s*\*\*[_\s]+\*\*\s*(.+)')
RE_TRANSLATE_ITEM = re.compile(r'[-•]\s*[""«](.+?)[""»]\s*→')


def _clean(text: str) -> str:
    """Strip markdown bold/italic markers and excessive whitespace."""
    t = text.strip()
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    t = re.sub(r'\*(.+?)\*', r'\1', t)
    return t.strip()


def _extract_between(text: str, start_pattern: str, stop_patterns: list[str]) -> str:
    """Extract text between a start header and the next matching stop header."""
    start_match = re.search(start_pattern, text, re.MULTILINE | re.IGNORECASE)
    if not start_match:
        return ""
    start_pos = start_match.end()

    end_pos = len(text)
    for sp in stop_patterns:
        m = re.search(sp, text[start_pos:], re.MULTILINE | re.IGNORECASE)
        if m:
            end_pos = min(end_pos, start_pos + m.start())
    return text[start_pos:end_pos].strip()


def _parse_theory_sections(lesson_text: str) -> list[dict]:
    """Extract numbered theory sections as rule cards."""
    cards = []
    # Match headers like: ### 1. 💡 Title  or  ### 2. 🔍 Title
    header_re = re.compile(
        r'^#{2,3}\s+(?:\*\*)?(\d+)[\.\)]\s*(.+?)(?:\*\*)?$',
        re.MULTILINE,
    )
    matches = list(header_re.finditer(lesson_text))
    stop_headers = [
        r'^#{2,3}\s+', r'^---\s*$',
    ]

    for i, m in enumerate(matches):
        title = _clean(m.group(2))
        # Skip if it's the expert corner header
        if 'coin des experts' in title.lower() or 'expert' in title.lower():
            continue
        start = m.end()
        # Find end (next numbered section, or next ## header, or ---)
        end = len(lesson_text)
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            for sp in stop_headers:
                sm = re.search(sp, lesson_text[start:], re.MULTILINE)
                if sm:
                    end = min(end, start + sm.start())

        content = lesson_text[start:end].strip()
        # Remove trailing ---
        content = re.sub(r'\n---\s*$', '', content).strip()

        # Extract inline examples (bold Arabic text with parenthetical French)
        examples = []
        ex_re = re.compile(r'\*\*(\S[\u0600-\u06FF\s\u064B-\u065F]+\S?)\*\*\s*\(?[""«]?([^)""»\n]+)[)""»]?')
        for ex in ex_re.finditer(content):
            examples.append({
                "ar": ex.group(1).strip(),
                "fr": ex.group(2).strip(),
                "translit": None,
            })

        cards.append({
            "type": "rule",
            "title_fr": title,
            "content_fr": content,
            "content_ar": None,
            "examples": examples if examples else [],
        })

    return cards


def _parse_expert_corner(lesson_text: str) -> dict | None:
    """Extract the coin des experts section."""
    patterns = [
        r'^#{2,3}\s+(?:\*\*)?(?:🎓\s*)?(?:\d+[\.\)]\s*)?(?:Le\s+)?[Cc]oin\s+des\s+[Ee]xperts?',
        r'^#{2,3}\s+(?:\*\*)?(?:🎓\s*)?(?:\d+[\.\)]\s*)?Analyse\s+[Ss]cientifique',
    ]
    for pat in patterns:
        m = re.search(pat, lesson_text, re.MULTILINE | re.IGNORECASE)
        if m:
            start = m.end()
            # Find end
            end = len(lesson_text)
            for sp in [r'^#{2,3}\s+', r'^---\s*$']:
                sm = re.search(sp, lesson_text[start:], re.MULTILINE)
                if sm:
                    end = min(end, start + sm.start())
            content = lesson_text[start:end].strip()
            content = re.sub(r'\n---\s*$', '', content).strip()
            if content:
                return {
                    "type": "expert_corner",
                    "title_fr": "Le coin des experts",
                    "content_fr": content,
                }
    return None


def _parse_pronunciation(lesson_text: str) -> dict | None:
    """Extract pronunciation items from 🔊 audio lines."""
    section_text = _extract_between(
        lesson_text,
        r'^#{2,3}\s+(?:\*\*)?(?:🔊\s*)?Prononciation',
        [r'^#{2,3}\s+', r'^---\s*$'],
    )
    if not section_text:
        # Try to find audio lines anywhere
        items = []
        for m in RE_AUDIO_LINE.finditer(lesson_text):
            items.append({"ar": m.group(1).strip(), "translit": "", "note": m.group(2).strip()})
        if items:
            return {"type": "pronunciation", "items": items}
        return None

    items = []
    for m in RE_AUDIO_LINE.finditer(section_text):
        items.append({"ar": m.group(1).strip(), "translit": "", "note": m.group(2).strip()})

    # Fallback: lines starting with 🔊
    if not items:
        for line in section_text.split('\n'):
            line = line.strip()
            if line.startswith('🔊'):
                text = line.replace('🔊', '').strip()
                items.append({"ar": "", "translit": "", "note": text})

    if items:
        return {"type": "pronunciation", "items": items}
    return None


def _parse_examples_table(lesson_text: str) -> dict | None:
    """Extract the examples practice table."""
    section_text = _extract_between(
        lesson_text,
        r'^#{2,3}\s+(?:\*\*)?(?:📝\s*)?Exemples',
        [r'^#{2,3}\s+', r'^---\s*$'],
    )
    if not section_text:
        return None

    rows = []
    for m in RE_TABLE_ROW.finditer(section_text):
        ar = _clean(m.group(1))
        fr = _clean(m.group(2))
        analysis = _clean(m.group(3))
        if ar and fr and 'Arabe' not in ar:  # Skip header row
            rows.append({"ar": ar, "fr": fr, "analysis": analysis})

    # Also try non-bold table rows
    if not rows:
        for m in re.finditer(r'^\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', section_text, re.MULTILINE):
            ar = _clean(m.group(1))
            fr = _clean(m.group(2))
            analysis = _clean(m.group(3))
            if ar and fr and 'Arabe' not in ar and '---' not in ar:
                rows.append({"ar": ar, "fr": fr, "analysis": analysis})

    if rows:
        return {"type": "examples_table", "rows": rows}
    return None


def _parse_mise_en_situation(lesson_text: str) -> dict | None:
    """Extract mise en situation paragraph."""
    section_text = _extract_between(
        lesson_text,
        r'^#{2,3}\s+(?:\*\*)?(?:🎬\s*)?Mise\s+en\s+[Ss]ituation',
        [r'^#{2,3}\s+', r'^---\s*$'],
    )
    if section_text:
        return {"type": "mise_en_situation", "content_fr": section_text}
    return None


def _parse_dialogue(lesson_text: str) -> dict | None:
    """Extract dialogue with situation and speaker lines."""
    section_text = _extract_between(
        lesson_text,
        r'^#{2,3}\s+(?:\*\*)?(?:💬\s*)?Mini[- ]?[Dd]ialogue',
        [r'^#{2,3}\s+', r'^---\s*$'],
    )
    if not section_text:
        return None

    # Extract situation
    situation = None
    sit_m = re.search(r'>\s*\*\*Situation\s*:?\*\*\s*:?\s*(.+)', section_text, re.IGNORECASE)
    if not sit_m:
        sit_m = re.search(r'>\s*\*\*(.+?)\*\*', section_text)
    if sit_m:
        situation = _clean(sit_m.group(1))

    # Extract dialogue lines: **speaker :** arabic text (french text)
    lines = []
    for m in RE_DIALOGUE_LINE.finditer(section_text):
        speaker = m.group(1).strip().rstrip(':').strip()
        rest = m.group(2).strip()

        # Skip "Situation" lines
        if 'situation' in speaker.lower():
            continue

        # Extract French translation from parentheses
        french = ""
        fr_m = re.search(r'\((.+?)\)', rest)
        if fr_m:
            french = _clean(fr_m.group(1))
            arabic = rest[:fr_m.start()].strip().rstrip('.')
        else:
            arabic = rest

        arabic = _clean(arabic)
        if arabic and speaker:
            lines.append({
                "speaker_ar": speaker,
                "arabic": arabic,
                "french": french,
            })

    if lines:
        return {"situation": situation, "lines": lines}
    return None


def _parse_exercises(lesson_text: str) -> list[dict]:
    """Parse exercises of production active."""
    section_text = _extract_between(
        lesson_text,
        r'^#{2,3}\s+(?:\*\*)?(?:✍️\s*)?Exercices\s+de\s+[Pp]roduction',
        [r'^#{2,3}\s+', r'^#{1,2}\s+', r'^---\s*$'],
    )
    if not section_text:
        return []

    exercises = []

    # Split by exercise number: **1. ...**  or  **N. ...**
    ex_blocks = re.split(r'\*\*(\d+)\.\s*(.+?)\*\*', section_text)

    i = 1
    while i < len(ex_blocks) - 1:
        num = ex_blocks[i]
        title = ex_blocks[i + 1].strip()
        body = ex_blocks[i + 2] if i + 2 < len(ex_blocks) else ""
        i += 3

        title_lower = title.lower()

        if 'remettez' in title_lower or 'ordre' in title_lower or 'reorder' in title_lower:
            # REORDER exercise
            # Parse: word1 / word2 → answer
            for line in body.split('\n'):
                line = line.strip()
                if '/' in line and ('→' in line or '➡' in line):
                    parts = re.split(r'→|➡', line)
                    words_part = parts[0].strip()
                    words = [w.strip().strip('*_') for w in words_part.split('/') if w.strip().strip('*_')]
                    if words:
                        exercises.append({
                            "type": "REORDER",
                            "prompt_fr": _clean(title),
                            "words": words,
                            "answer": list(reversed(words)),  # Usually reversed
                        })
                elif '/' in line:
                    words = [w.strip().strip('*_') for w in line.split('/') if w.strip().strip('*_')]
                    if words and any(re.search(r'[\u0600-\u06FF]', w) for w in words):
                        exercises.append({
                            "type": "REORDER",
                            "prompt_fr": _clean(title),
                            "words": words,
                            "answer": list(reversed(words)),
                        })

        elif 'complétez' in title_lower or 'compléter' in title_lower or 'fill' in title_lower:
            # FILL_BLANK exercise
            items = []
            for line in body.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    line = line.lstrip('-•').strip()
                    # Pattern: **___** word (hint)
                    m = re.search(r'\*\*[_\s]+\*\*\s*(.+)', line)
                    if m:
                        sentence = m.group(1).strip()
                        items.append({"sentence": f"___ {sentence}", "answer": ""})
                    else:
                        items.append({"sentence": line, "answer": ""})

            if items:
                exercises.append({
                    "type": "FILL_BLANK",
                    "prompt_fr": _clean(title),
                    "items": items,
                })

        elif 'traduisez' in title_lower or 'translat' in title_lower:
            # TRANSLATE exercise
            items = []
            for line in body.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('•'):
                    line = line.lstrip('-•').strip()
                    # Pattern: "French text" → ___
                    m = re.search(r'[""«](.+?)[""»]\s*→', line)
                    if m:
                        items.append({"prompt_fr": m.group(1).strip(), "answer_ar": ""})

            if items:
                exercises.append({
                    "type": "TRANSLATE",
                    "prompt_fr": _clean(title),
                    "items": items,
                })

        elif 'class' in title_lower or 'bonus' in title_lower or 'masculin' in title_lower or 'féminin' in title_lower:
            # CLASSIFY exercise
            items = []
            # Look for words separated by — or /
            for line in body.split('\n'):
                line = line.strip()
                if '—' in line or '–' in line:
                    words = re.split(r'\s*[—–]\s*', line)
                    for w in words:
                        w = w.strip().strip('*_')
                        if w and re.search(r'[\u0600-\u06FF]', w):
                            # Guess category based on ta marbuta
                            has_ta_marbuta = 'ة' in w
                            items.append({
                                "word": w,
                                "category": "Féminin" if has_ta_marbuta else "Masculin",
                            })

            if items:
                exercises.append({
                    "type": "CLASSIFY",
                    "prompt_fr": _clean(title),
                    "categories": ["Masculin", "Féminin"],
                    "items": items,
                })

    return exercises


def _extract_questions_from_json(raw: str, prefix: str) -> list[dict]:
    """Parse a JSON block that may be an object with 'quizzes'/'questions' or a bare list."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    questions: list[dict] = []
    if isinstance(data, list):
        questions = data
    elif isinstance(data, dict):
        # Try several known keys
        if "quizzes" in data:
            # Each quiz has lesson_id and questions
            for quiz in data["quizzes"]:
                questions.extend(quiz.get("questions", []))
        elif "questions" in data:
            questions = data["questions"]
        else:
            return []

    result = []
    for i, q in enumerate(questions):
        result.append({
            "id": q.get("id", f"{prefix}_q{i+1}"),
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct": q.get("correct", 0),
            "explanation": q.get("explanation"),
        })
    return result


def _extract_flashcards_from_json(raw: str, prefix: str) -> list[dict]:
    """Parse a JSON block that may be an object with 'flashcards'/'cards' or a bare list."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    cards: list[dict] = []
    if isinstance(data, list):
        cards = data
    elif isinstance(data, dict):
        if "flashcards" in data:
            cards = data["flashcards"]
        elif "cards" in data:
            cards = data["cards"]
        else:
            return []

    result = []
    for i, c in enumerate(cards):
        result.append({
            "id": c.get("id", f"{prefix}_{i+1}"),
            "front_ar": c.get("front_ar", c.get("front", c.get("arabic", ""))),
            "back_fr": c.get("back_fr", c.get("back", c.get("french", c.get("translation", "")))),
            "category": c.get("category", c.get("type")),
            "example_ar": c.get("example_ar", c.get("example")),
            "example_fr": c.get("example_fr"),
        })
    return result


def _parse_quiz_json(full_text: str, part_number: int) -> list[dict]:
    """Extract quiz questions from JSON blocks for a specific part."""
    # Very flexible pattern to match various header formats
    pattern = rf'#{1,2}\s+(?:\S+\s+)?QUIZ\s+(?:JSON\s+)?[-—]?\s*PART(?:IE)?\s*{part_number}\b'
    m = re.search(pattern, full_text, re.IGNORECASE)
    if not m:
        # Try alternative: "QUIZ JSON PART N" without # prefix
        pattern2 = rf'QUIZ\s+(?:JSON\s+)?[-—]?\s*PART(?:IE)?\s*{part_number}\b'
        m = re.search(pattern2, full_text, re.IGNORECASE)
    if not m:
        return []

    rest = full_text[m.start():]
    json_match = RE_JSON_BLOCK.search(rest)
    if not json_match:
        return []

    return _extract_questions_from_json(json_match.group(1), f"p{part_number}")


def _parse_flashcard_json(full_text: str, part_number: int) -> list[dict]:
    """Extract flashcards from JSON blocks for a specific part."""
    pattern = rf'#{1,2}\s+(?:\S+\s+)?FLASHCARD\s+(?:JSON\s+)?[-—]?\s*PART(?:IE)?\s*{part_number}\b'
    m = re.search(pattern, full_text, re.IGNORECASE)
    if not m:
        pattern2 = rf'FLASHCARD\s+(?:JSON\s+)?[-—]?\s*PART(?:IE)?\s*{part_number}\b'
        m = re.search(pattern2, full_text, re.IGNORECASE)
    if not m:
        return []

    rest = full_text[m.start():]
    json_match = RE_JSON_BLOCK.search(rest)
    if not json_match:
        return []

    return _extract_flashcards_from_json(json_match.group(1), f"fc_p{part_number}")


def _parse_lesson_quiz_json(lesson_text: str, lesson_number: int) -> list[dict]:
    """Extract quiz questions embedded directly in a lesson (lessons 22-23 style)."""
    pattern = r'(?:Quiz|QUIZ)\s+(?:de\s+)?[Vv]alidation'
    m = re.search(pattern, lesson_text, re.IGNORECASE)
    if not m:
        return []

    rest = lesson_text[m.start():]
    json_match = RE_JSON_BLOCK.search(rest)
    if not json_match:
        return []

    return _extract_questions_from_json(json_match.group(1), f"l{lesson_number}")


def parse_v2() -> dict:
    """Parse the full MD file and return V2 structured content."""
    text = MD_PATH.read_text(encoding="utf-8")

    # Find all lesson positions
    lesson_matches = list(RE_LESSON.finditer(text))
    if not lesson_matches:
        raise ValueError("No lessons found in MD file")

    lessons: dict[str, dict] = {}

    for idx, match in enumerate(lesson_matches):
        lesson_num = int(match.group(1))
        title = match.group(2).strip()

        # Get lesson text (until next lesson or end of file)
        start = match.start()
        end = lesson_matches[idx + 1].start() if idx + 1 < len(lesson_matches) else len(text)
        lesson_text = text[start:end]

        part_num = LESSON_TO_PART.get(lesson_num, 1)

        # Objective
        obj_m = RE_OBJECTIVE.search(lesson_text)
        objective = _clean(obj_m.group(1)) if obj_m else None

        # Build discovery cards
        discovery_cards: list[dict] = []

        # 1. Theory sections (rules)
        rules = _parse_theory_sections(lesson_text)
        discovery_cards.extend(rules)

        # 2. Expert corner
        expert = _parse_expert_corner(lesson_text)
        if expert:
            discovery_cards.append(expert)

        # 3. Pronunciation
        pronun = _parse_pronunciation(lesson_text)
        if pronun:
            discovery_cards.append(pronun)

        # 4. Examples table
        examples = _parse_examples_table(lesson_text)
        if examples:
            discovery_cards.append(examples)

        # 5. Mise en situation
        mise = _parse_mise_en_situation(lesson_text)
        if mise:
            discovery_cards.append(mise)

        # Dialogue
        dialogue = _parse_dialogue(lesson_text)

        # Exercises
        exercises = _parse_exercises(lesson_text)

        # Quiz (try lesson-embedded first, then part-level)
        quiz_questions = _parse_lesson_quiz_json(lesson_text, lesson_num)
        if not quiz_questions:
            # Will be filled in post-processing from part-level quizzes
            quiz_questions = []

        # Flashcards (will be filled from part-level)
        flashcards: list[dict] = []

        lessons[str(lesson_num)] = {
            "lesson_number": lesson_num,
            "title_fr": title,
            "title_ar": "",
            "part_number": part_num,
            "part_name": PART_NAMES.get(part_num, ""),
            "objective": objective,
            "discovery_cards": discovery_cards,
            "dialogue": dialogue,
            "exercises": exercises,
            "quiz_questions": quiz_questions,
            "flashcards": flashcards,
        }

    # Post-process: distribute part-level quizzes and flashcards to lessons
    for part_num in range(1, 8):
        quiz_qs = _parse_quiz_json(text, part_num)
        flash_cs = _parse_flashcard_json(text, part_num)

        # Find lessons in this part
        part_lessons = [n for n, p in LESSON_TO_PART.items() if p == part_num]
        part_lessons.sort()

        # Distribute quiz questions evenly across lessons that don't have their own
        if quiz_qs:
            lessons_needing_quiz = [
                n for n in part_lessons
                if str(n) in lessons and not lessons[str(n)]["quiz_questions"]
            ]
            if lessons_needing_quiz:
                per_lesson = max(1, len(quiz_qs) // len(lessons_needing_quiz))
                for i, ln in enumerate(lessons_needing_quiz):
                    start_idx = i * per_lesson
                    end_idx = start_idx + per_lesson if i < len(lessons_needing_quiz) - 1 else len(quiz_qs)
                    lessons[str(ln)]["quiz_questions"] = quiz_qs[start_idx:end_idx]

        # Distribute flashcards
        if flash_cs:
            if part_lessons:
                per_lesson = max(1, len(flash_cs) // len(part_lessons))
                for i, ln in enumerate(part_lessons):
                    if str(ln) in lessons:
                        start_idx = i * per_lesson
                        end_idx = start_idx + per_lesson if i < len(part_lessons) - 1 else len(flash_cs)
                        lessons[str(ln)]["flashcards"] = flash_cs[start_idx:end_idx]

    return lessons


def generate_v2_json() -> None:
    """Parse and write lessons_content_v2.json."""
    lessons = parse_v2()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(lessons, f, ensure_ascii=False, indent=2)

    # Summary
    print(f"✅ Generated {OUT_PATH.name} — {len(lessons)} lessons\n")
    for key in sorted(lessons.keys(), key=int):
        l = lessons[key]
        print(
            f"  Leçon {l['lesson_number']:2d} | "
            f"cards: {len(l['discovery_cards']):2d} | "
            f"dialogue: {len(l.get('dialogue', {}).get('lines', [])) if l.get('dialogue') else 0:2d} lines | "
            f"exercises: {len(l['exercises']):2d} | "
            f"quiz: {len(l['quiz_questions']):2d} | "
            f"flashcards: {len(l['flashcards']):2d}"
        )


if __name__ == "__main__":
    generate_v2_json()
