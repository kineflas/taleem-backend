"""
Admin Audio Recording — standalone HTML page + API endpoints.

Protected by JWT + email whitelist. Only whitelisted users can access.
Serves a standalone HTML page at GET /admin/audio and provides:
  - GET  /api/admin/audio/status    → list all audio_ids with recorded/missing
  - POST /api/admin/audio/{audio_id} → upload recorded audio (webm → mp3)
  - DELETE /api/admin/audio/{audio_id} → remove a recorded audio file
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import HTMLResponse, JSONResponse

from ..core.dependencies import CurrentUser

logger = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────────────────────
ADMIN_EMAILS = [
    "khalidborntocode@gmail.com",
]

AUDIO_DIR = Path("static/audio")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

router = APIRouter(tags=["Admin Audio"])


# ── Admin guard ──────────────────────────────────────────────────────────────

def require_admin(current_user: CurrentUser):
    """Check that the authenticated user's email is in the admin whitelist."""
    if current_user.email not in ADMIN_EMAILS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    return current_user


AdminUser = Annotated[CurrentUser, Depends(require_admin)]


# ── Helpers ──────────────────────────────────────────────────────────────────

def _extract_audio_ids_from_json() -> dict[str, list[dict]]:
    """
    Scan all JSON data files and extract every audio_id.
    Returns dict grouped by source: { "odyssee_lettres/lesson_1": [ {audio_id, context}, ... ] }
    """
    results: dict[str, list[dict]] = {}

    # --- Odyssée des Lettres ---
    odyssee_path = DATA_DIR / "odyssee_lettres.json"
    if odyssee_path.exists():
        with open(odyssee_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for lesson_key, lesson in data.items():
            group = f"odyssee/lesson_{lesson_key}"
            entries = []

            # Letters
            for letter in lesson.get("letters", []):
                if letter.get("audio_id"):
                    entries.append({
                        "audio_id": letter["audio_id"],
                        "context": f"Lettre: {letter.get('name_fr', '')} ({letter.get('name_ar', '')})",
                        "text_ar": letter.get("name_ar", ""),
                    })
                # Syllables (dict of dicts keyed by vowel name)
                syllabes = letter.get("syllabes", {})
                if isinstance(syllabes, dict):
                    for vowel, syl in syllabes.items():
                        if isinstance(syl, dict) and syl.get("audio_id"):
                            entries.append({
                                "audio_id": syl["audio_id"],
                                "context": f"Syllabe ({vowel}): {syl.get('glyph', '')} — {syl.get('son', '')}",
                                "text_ar": syl.get("glyph", ""),
                            })

            # Ecoute sequence
            ecoute = lesson.get("ecoute", {})
            for item in ecoute.get("sequence", []):
                if item.get("audio_id"):
                    entries.append({
                        "audio_id": item["audio_id"],
                        "context": f"Écoute: {item.get('text_ar', '')}",
                        "text_ar": item.get("text_ar", ""),
                    })

            # Exercises
            for ex in lesson.get("exercises", []):
                _extract_exercise_audio(ex, entries)

            # Mini lecture
            ml = lesson.get("mini_lecture", {})
            if ml.get("audio_id"):
                entries.append({
                    "audio_id": ml["audio_id"],
                    "context": f"Mini-lecture: {ml.get('text_ar', '')}",
                    "text_ar": ml.get("text_ar", ""),
                })
            for item in ml.get("items", []):
                if item.get("audio_id"):
                    entries.append({
                        "audio_id": item["audio_id"],
                        "context": f"Karaoke: {item.get('text_ar', '')}",
                        "text_ar": item.get("text_ar", ""),
                    })

            # Quiz
            for q in lesson.get("quiz_questions", []):
                if q.get("audio_id"):
                    entries.append({
                        "audio_id": q["audio_id"],
                        "context": f"Quiz: {q.get('question_fr', '')}",
                        "text_ar": q.get("text_ar", ""),
                    })

            # Flashcards
            for fc in lesson.get("flashcards", []):
                if fc.get("audio_id"):
                    entries.append({
                        "audio_id": fc["audio_id"],
                        "context": f"Flashcard: {fc.get('front', '')}",
                        "text_ar": fc.get("text_ar", fc.get("front", "")),
                    })

            if entries:
                results[group] = entries

    return results


def _extract_exercise_audio(ex: dict, entries: list):
    """Extract audio_ids from a single exercise dict."""
    if ex.get("audio_id"):
        entries.append({
            "audio_id": ex["audio_id"],
            "context": f"Exercise ({ex.get('type', '')}): {ex.get('instruction_fr', '')}",
            "text_ar": ex.get("text_ar", ""),
        })
    # Items inside exercises
    for item in ex.get("items", []):
        if isinstance(item, dict) and item.get("audio_id"):
            entries.append({
                "audio_id": item["audio_id"],
                "context": f"Exercise item: {item.get('label', item.get('son', ''))}",
                "text_ar": item.get("text_ar", item.get("son", "")),
            })
    # Options with audio
    for opt in ex.get("options", []):
        if isinstance(opt, dict) and opt.get("audio_id"):
            entries.append({
                "audio_id": opt["audio_id"],
                "context": f"Option: {opt.get('label', '')}",
                "text_ar": opt.get("text_ar", opt.get("label", "")),
            })


def _get_recorded_set() -> set[str]:
    """Return set of audio_ids that already have a .mp3 file."""
    recorded = set()
    if AUDIO_DIR.exists():
        for f in AUDIO_DIR.rglob("*.mp3"):
            recorded.add(f.stem)
    return recorded


# ── API endpoints ────────────────────────────────────────────────────────────

@router.get("/api/admin/audio/status")
def audio_status(admin: AdminUser):
    """Return all audio_ids grouped by source, with recorded/missing status."""
    groups = _extract_audio_ids_from_json()
    recorded = _get_recorded_set()

    total = 0
    done = 0
    response_groups = []

    for group_name, entries in sorted(groups.items()):
        items = []
        for entry in entries:
            aid = entry["audio_id"]
            is_recorded = aid in recorded
            total += 1
            if is_recorded:
                done += 1
            items.append({
                "audio_id": aid,
                "context": entry["context"],
                "text_ar": entry.get("text_ar", ""),
                "recorded": is_recorded,
            })
        response_groups.append({
            "group": group_name,
            "items": items,
        })

    return {
        "total": total,
        "recorded": done,
        "missing": total - done,
        "groups": response_groups,
    }


@router.post("/api/admin/audio/{audio_id}")
async def upload_audio(audio_id: str, admin: AdminUser, file: UploadFile = File(...)):
    """
    Upload an audio recording for a given audio_id.
    Accepts webm/wav/ogg — converts to mp3 via ffmpeg.
    Also accepts mp3 directly.
    """
    if not audio_id or "/" in audio_id or "\\" in audio_id:
        raise HTTPException(status_code=400, detail="audio_id invalide")

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    target = AUDIO_DIR / f"{audio_id}.mp3"

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    # If already mp3, save directly
    ct = file.content_type or ""
    if "mp3" in ct or "mpeg" in ct:
        target.write_bytes(content)
        logger.info("Audio saved (mp3 direct): %s", audio_id)
        return {"status": "ok", "audio_id": audio_id, "format": "mp3"}

    # Otherwise, convert via ffmpeg
    tmp_in = AUDIO_DIR / f"_tmp_{audio_id}.webm"
    try:
        tmp_in.write_bytes(content)
        result = subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(tmp_in),
                "-ac", "1", "-ar", "44100", "-b:a", "128k",
                str(target),
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            logger.error("ffmpeg error: %s", result.stderr)
            raise HTTPException(status_code=500, detail=f"Conversion échouée: {result.stderr[:200]}")
    finally:
        tmp_in.unlink(missing_ok=True)

    logger.info("Audio saved (converted): %s", audio_id)
    return {"status": "ok", "audio_id": audio_id, "format": "mp3"}


@router.delete("/api/admin/audio/{audio_id}")
def delete_audio(audio_id: str, admin: AdminUser):
    """Delete a recorded audio file."""
    target = AUDIO_DIR / f"{audio_id}.mp3"
    if not target.exists():
        raise HTTPException(status_code=404, detail="Fichier non trouvé")
    target.unlink()
    return {"status": "deleted", "audio_id": audio_id}


# ── Serve the standalone HTML page ───────────────────────────────────────────

HTML_PATH = Path(__file__).resolve().parent.parent.parent / "static" / "admin_audio.html"


@router.get("/admin/audio", response_class=HTMLResponse)
def admin_audio_page():
    """Serve the standalone admin audio recording page."""
    if not HTML_PATH.exists():
        raise HTTPException(status_code=404, detail="Page admin non trouvée")
    return HTMLResponse(content=HTML_PATH.read_text(encoding="utf-8"))
