"""
Parser for extracting rich lesson PROSE content from the Medine Tome 1 MD file.

Unlike medine_tome1_parser.py which extracts JSON blocks (quizzes, flashcards),
this parser extracts the textual lesson content:
  - Theory sections (numbered ### headers)
  - Le coin des experts
  - Mini-Dialogue
  - Exemples (tables)
  - Exercices de production active
  - Mise en situation
  - Objectif

The output per lesson is a dict that maps directly to the CurriculumItem.extra_data
fields: explanation_sections, examples, vocab, dialogue, etc.
"""
import re
from pathlib import Path
from typing import Any


def _split_lessons(md_text: str) -> dict[int, str]:
    """Split the MD into per-lesson raw text blocks.

    Handles ALL header variants in the MD file:
      # 🟢 LEÇON 5 : L'Annexion           (lessons 1-8)
      # 🎨 Leçon 9 : La Qualification      (lessons 9-12, various emojis)
      # LEÇON 13 : Le Pluriel              (lessons 13-15, no emoji)
      ## LEÇON 16 : Le Pluriel des Objets  (lessons 16-21, ## level)
      ## 🎓 LEÇON 22 : L'Action            (lessons 22-23, ## with emoji)
    """
    # Pattern: 1-2 hashes, optional emoji, Leçon/LEÇON N, colon/dash, title
    pattern = r'^#{1,2}\s+(?:\S+\s+)?[Ll][Ee][Çç][Oo][Nn]\s+(\d+)\s*[:\—–-]\s*(.+)$'

    lessons: dict[int, dict] = {}
    current_num = None
    current_title = ""
    current_lines: list[str] = []

    for line in md_text.split('\n'):
        match = re.match(pattern, line, re.IGNORECASE)
        if match:
            # Save previous lesson
            if current_num is not None:
                lessons[current_num] = {
                    'title': current_title,
                    'raw': '\n'.join(current_lines),
                }
            current_num = int(match.group(1))
            current_title = match.group(2).strip()
            current_lines = []
        elif current_num is not None:
            current_lines.append(line)

    # Save last lesson
    if current_num is not None:
        lessons[current_num] = {
            'title': current_title,
            'raw': '\n'.join(current_lines),
        }

    return lessons


def _extract_objective(raw: str) -> str | None:
    """Extract the > **Objectif :** line."""
    match = re.search(r'>\s*\*\*Objectif\s*:\*\*\s*(.+)', raw)
    return match.group(1).strip() if match else None


def _extract_sections(raw: str) -> list[dict]:
    """Extract numbered sections as theory content.

    Matches patterns like:
      ### 1. 💡 Le concept d'Annexion       (lessons 1-8)
      ## 1. 👥 Le duo Nom + Adjectif        (lessons 9-12, ## level)
      ### Explication Grammaticale Complète  (lessons 16-21, unnumbered ###)
      ### 🎓 Le coin des experts             (all lessons)
    """
    # Split by ## or ### headers (with optional number prefix)
    pattern = r'^#{2,3}\s+(?:\d+\.\s*)?(.+)$'
    sections = []
    current_title = None
    current_lines: list[str] = []

    for line in raw.split('\n'):
        match = re.match(pattern, line)
        if match:
            # Save previous section
            if current_title is not None:
                content = '\n'.join(current_lines).strip()
                if content:
                    sections.append({
                        'title': current_title,
                        'content': content,
                    })
            current_title = match.group(1).strip()
            # Remove emoji prefix (broad Unicode emoji range)
            current_title = re.sub(r'^[\U0001F300-\U0001F9FF\u2600-\u27BF\u2702-\u27B0]+\s*', '', current_title).strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    # Save last section
    if current_title is not None:
        content = '\n'.join(current_lines).strip()
        if content:
            sections.append({
                'title': current_title,
                'content': content,
            })

    return sections


def _categorize_sections(sections: list[dict]) -> dict:
    """Categorize sections into: theory, coin_experts, dialogue, examples, exercises, mise_en_situation."""
    result = {
        'theory_sections': [],
        'coin_experts': None,
        'dialogue': None,
        'dialogue_situation': None,
        'examples_table': None,
        'exercises': None,
        'mise_en_situation': None,
        'pronunciation': None,
    }

    for sec in sections:
        title_lower = sec['title'].lower()

        if 'coin des experts' in title_lower:
            result['coin_experts'] = sec['content']
        elif 'mini-dialogue' in title_lower or 'dialogue contextuel' in title_lower or 'dialogue' in title_lower:
            result['dialogue'] = sec['content']
        elif 'mise en situation' in title_lower:
            result['mise_en_situation'] = sec['content']
        elif 'exemples' in title_lower and ('pratiquer' in title_lower or 'production' not in title_lower):
            result['examples_table'] = sec['content']
        elif 'exercice' in title_lower or 'production active' in title_lower:
            result['exercises'] = sec['content']
        elif 'prononciation' in title_lower:
            result['pronunciation'] = sec['content']
        elif 'quiz de validation' in title_lower or 'quiz' in title_lower:
            # Skip quiz sections — handled separately by medine_tome1_parser
            pass
        elif 'résumé' in title_lower or 'sommaire' in title_lower:
            # Skip summary/table of contents sections
            pass
        else:
            # Regular theory section
            result['theory_sections'].append(sec)

    return result


def _parse_dialogue(dialogue_text: str) -> list[dict]:
    """Parse dialogue lines into structured format.

    Handles two formats:

    Format A (lessons 1-8): inline translation
      **الْمُوَظَّفُ :** اسْمُكَ؟ (*Ton nom ?*)

    Format B (lessons 9+): paired lines (Arabic then French)
      **البائع :** هَذِهِ سَيَّارَةٌ جَدِيدَةٌ
      **Le vendeur :** C'est une voiture nouvelle et belle.
    """
    if not dialogue_text:
        return []

    lines = []
    # Extract situation line (> **Situation :** ... or **(context)**)
    situation_match = re.search(r'>\s*\*\*Situation\s*:\*\*\s*(.+)', dialogue_text)
    if not situation_match:
        situation_match = re.search(r'^\*\*\((.+?)\)\*\*', dialogue_text, re.MULTILINE)
    situation = situation_match.group(1).strip() if situation_match else None

    # Extract all **Speaker :** content lines
    pattern = r'\*\*([^*]+)\*\*\s*:\s*(.+)'
    raw_lines = []
    for line in dialogue_text.split('\n'):
        match = re.search(pattern, line)
        if match:
            speaker = match.group(1).strip()
            content = match.group(2).strip()
            raw_lines.append((speaker, content))

    # Try Format A first: check if any line has (*translation*) inline
    has_inline_translation = any(re.search(r'\(\*.*?\*\)', content) for _, content in raw_lines)

    if has_inline_translation:
        # Format A: **speaker_ar :** arabic (*french*)
        for speaker, content in raw_lines:
            trans_match = re.search(r'\(\*(.+?)\*\)', content)
            french = trans_match.group(1).strip() if trans_match else ''
            arabic = re.sub(r'\(\*.*?\*\)', '', content).strip()
            lines.append({
                'speaker_ar': speaker,
                'arabic': arabic,
                'french': french,
            })
    else:
        # Format B: paired lines — Arabic speaker then French speaker
        i = 0
        while i < len(raw_lines):
            speaker, content = raw_lines[i]
            # Check if this line has Arabic content (Arabic Unicode chars)
            has_arabic = bool(re.search(r'[\u0600-\u06FF]', content))

            if has_arabic:
                arabic = content
                french = ''
                speaker_ar = speaker
                # Look for the next line as French translation
                if i + 1 < len(raw_lines):
                    next_speaker, next_content = raw_lines[i + 1]
                    next_has_arabic = bool(re.search(r'[\u0600-\u06FF]{3,}', next_content))
                    if not next_has_arabic:
                        french = next_content
                        i += 1  # Skip the French line
                lines.append({
                    'speaker_ar': speaker_ar,
                    'arabic': arabic,
                    'french': french,
                })
            i += 1

    result = {'lines': lines}
    if situation:
        result['situation'] = situation
    return result


def _parse_examples_table(table_text: str) -> list[dict]:
    """Parse markdown table into structured examples.

    | **Arabe** | **Français** | **Structure** |
    | --- | --- | --- |
    | **كِتَابُ أَحْمَدَ** | Le livre d'Ahmed | Nom + Pronom masculin |
    """
    if not table_text:
        return []

    examples = []
    for line in table_text.split('\n'):
        # Skip header row and separator
        if '---' in line or not line.strip().startswith('|'):
            continue

        cells = [c.strip() for c in line.split('|')[1:-1]]  # Remove empty first/last
        if len(cells) < 2:
            continue

        arabic = re.sub(r'\*\*', '', cells[0]).strip()
        french = re.sub(r'\*\*', '', cells[1]).strip()

        if not arabic or arabic.lower() in ('arabe', 'arab', '**arabe**'):
            continue  # Skip header

        example = {
            'arabic': arabic,
            'translation_fr': french,
        }
        if len(cells) >= 3:
            example['grammatical_note_fr'] = re.sub(r'\*\*', '', cells[2]).strip()

        examples.append(example)

    return examples


def parse_lesson_content(md_path: str) -> dict[int, dict[str, Any]]:
    """
    Parse the full MD file and return enriched content per lesson.

    Returns:
        {
            1: {
                'objective': "...",
                'explanation_sections': [{title_fr, content_fr, content_ar, tip_fr}],
                'coin_experts': "...",
                'dialogue': {situation, lines: [{speaker_ar, arabic, french}]},
                'mise_en_situation': "...",
                'examples_md': [{arabic, translation_fr, grammatical_note_fr}],
                'exercises_md': "...",
                'pronunciation': "...",
            },
            2: {...},
            ...
        }
    """
    md_text = Path(md_path).read_text(encoding='utf-8')
    lessons_raw = _split_lessons(md_text)

    result = {}
    for num, data in sorted(lessons_raw.items()):
        raw = data['raw']

        # Extract objective
        objective = _extract_objective(raw)

        # Extract and categorize sections
        all_sections = _extract_sections(raw)
        categorized = _categorize_sections(all_sections)

        # Build explanation_sections from theory sections
        explanation_sections = []
        for sec in categorized['theory_sections']:
            # Try to separate Arabic content from French
            content = sec['content']
            content_ar = None
            tip_fr = None

            # Look for Arabic blocks (lines with mostly Arabic chars)
            ar_lines = []
            fr_lines = []
            for line in content.split('\n'):
                # Simple heuristic: if line has Arabic chars, treat separately
                if re.search(r'[\u0600-\u06FF]{5,}', line) and not line.startswith('-') and not line.startswith('|'):
                    ar_lines.append(line)
                else:
                    fr_lines.append(line)

            content_fr = '\n'.join(fr_lines).strip()
            if ar_lines:
                content_ar = '\n'.join(ar_lines).strip()

            explanation_sections.append({
                'title_fr': sec['title'],
                'content_fr': content_fr,
                'content_ar': content_ar,
                'tip_fr': tip_fr,
            })

        # Parse dialogue
        dialogue = _parse_dialogue(categorized['dialogue']) if categorized['dialogue'] else None

        # Parse examples table
        examples_md = _parse_examples_table(categorized['examples_table']) if categorized['examples_table'] else []

        result[num] = {
            'objective': objective,
            'explanation_sections': explanation_sections,
            'coin_experts': categorized['coin_experts'],
            'dialogue': dialogue,
            'mise_en_situation': categorized['mise_en_situation'],
            'examples_md': examples_md,
            'exercises_md': categorized['exercises'],
            'pronunciation': categorized['pronunciation'],
        }

    print(f"✓ Parsed prose content for {len(result)} lessons")
    return result


if __name__ == "__main__":
    import sys, json
    md_path = sys.argv[1] if len(sys.argv) > 1 else "data/📚 Tome 1 Médine — Édition Optimisée.md"
    data = parse_lesson_content(md_path)
    for num, content in sorted(data.items()):
        sections = len(content['explanation_sections'])
        has_experts = '✓' if content['coin_experts'] else '✗'
        has_dialogue = '✓' if content['dialogue'] else '✗'
        has_examples = len(content['examples_md'])
        print(f"  Leçon {num:2d}: {sections} sections, experts={has_experts}, dialogue={has_dialogue}, {has_examples} exemples")
