#!/usr/bin/env python3
"""
generate_audio_timings.py — Injecte les vrais timestamps word-level
(quran-align / Husary) dans juz_amma_enriched.json.

N'utilise QUE la stdlib Python (pas de `requests`).

Usage:
  python scripts/generate_audio_timings.py                # applique
  python scripts/generate_audio_timings.py --dry-run      # preview sans écriture
  python scripts/generate_audio_timings.py --all-surahs   # traite tout Juz Amma (78-114)
"""

import argparse
import io
import json
import os
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

# ── Chemins ──────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "app" / "data"
ENRICHED_JSON = DATA_DIR / "juz_amma_enriched.json"
CACHE_DIR = SCRIPT_DIR / ".cache"

# ── Config quran-align ───────────────────────────────────────────────

QURAN_ALIGN_ZIP_URL = (
    "https://github.com/cpfair/quran-align/releases/download/"
    "release-2016-11-24/quran-align-data-2016-11-24.zip"
)
HUSARY_FILENAME = "Husary_64kbps.json"

# ── Juz Amma ─────────────────────────────────────────────────────────

JUZ_AMMA_RANGE = range(78, 115)


def load_enriched_json() -> list:
    with open(ENRICHED_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_enriched_json(data: list) -> None:
    with open(ENRICHED_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Fichier sauvegardé : {ENRICHED_JSON}")


# ══════════════════════════════════════════════════════════════════════
# Téléchargement et extraction quran-align
# ══════════════════════════════════════════════════════════════════════

def download_quran_align_data() -> list:
    """
    Télécharge le ZIP quran-align et extrait le JSON Husary.
    Utilise un cache local pour éviter de re-télécharger.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    cached_json = CACHE_DIR / HUSARY_FILENAME

    # Utiliser le cache si présent
    if cached_json.exists():
        print(f"📂 Cache trouvé : {cached_json}")
        with open(cached_json, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"📥 Téléchargement de quran-align data...")
    print(f"   URL: {QURAN_ALIGN_ZIP_URL}")

    req = Request(QURAN_ALIGN_ZIP_URL, headers={"User-Agent": "Taleem/1.0"})
    with urlopen(req, timeout=120) as resp:
        zip_bytes = resp.read()

    print(f"   Taille: {len(zip_bytes) // 1024} KB")

    # Extraire Husary JSON depuis le ZIP
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        husary_path = None
        for name in zf.namelist():
            if HUSARY_FILENAME in name:
                husary_path = name
                break

        if not husary_path:
            print(f"❌ {HUSARY_FILENAME} non trouvé dans le ZIP.")
            print(f"   Fichiers: {zf.namelist()}")
            sys.exit(1)

        print(f"   Extraction : {husary_path}")
        with zf.open(husary_path) as f:
            raw_data = json.load(f)

    # Sauvegarder en cache
    with open(cached_json, "w", encoding="utf-8") as f:
        json.dump(raw_data, f)
    print(f"   Cache sauvegardé : {cached_json}")

    return raw_data


# ══════════════════════════════════════════════════════════════════════
# Conversion des segments
# ══════════════════════════════════════════════════════════════════════

def convert_segments_to_timings(
    segments: list, word_count: int
) -> list:
    """
    Convertit les segments quran-align en audio_timing.

    quran-align: [[word_start_idx, word_end_idx, start_ms, end_ms], ...]
       → Les timestamps sont absolus dans l'audio de la sourate complète.
       → Pour des fichiers par verset (EveryAyah), on soustrait le
         timestamp du premier mot pour obtenir des temps relatifs.

    Sortie: [0.0, 0.45, 1.2, ...] en secondes, relatifs au début du verset.
    """
    if not segments or word_count == 0:
        return []

    # Référence = début du premier segment (= début du verset dans l'audio sourate)
    verse_start_ms = segments[0][2]

    word_timings = [None] * word_count

    for seg in segments:
        w_start = seg[0]   # 0-based, premier mot du segment
        w_end = seg[1]     # 0-based, mot APRÈS le dernier (exclusif)
        start_ms = seg[2]
        end_ms = seg[3]

        n_words = w_end - w_start
        if n_words <= 0:
            continue

        seg_duration = end_ms - start_ms
        for i in range(n_words):
            w_idx = w_start + i
            if 0 <= w_idx < word_count:
                # Distribuer uniformément si le segment couvre plusieurs mots
                word_ms = start_ms + (seg_duration * i // n_words)
                word_timings[w_idx] = round(
                    (word_ms - verse_start_ms) / 1000.0, 3
                )

    # Le premier mot doit toujours être à 0.0
    if word_timings[0] is not None:
        word_timings[0] = 0.0

    # Remplir les trous éventuels par interpolation linéaire
    for i in range(word_count):
        if word_timings[i] is None:
            # Trouver le prochain non-null
            prev_val = word_timings[i - 1] if i > 0 and word_timings[i - 1] is not None else 0.0
            next_val = None
            next_idx = i + 1
            while next_idx < word_count:
                if word_timings[next_idx] is not None:
                    next_val = word_timings[next_idx]
                    break
                next_idx += 1

            if next_val is not None and next_idx > i:
                # Interpolation linéaire
                step = (next_val - prev_val) / (next_idx - i + 1)
                word_timings[i] = round(prev_val + step, 3)
            else:
                # Fallback : +400ms
                word_timings[i] = round(prev_val + 0.4, 3)

    return word_timings


# ══════════════════════════════════════════════════════════════════════
# Pipeline principal
# ══════════════════════════════════════════════════════════════════════

def process_timings(dry_run: bool = False) -> None:
    """Pipeline complet : télécharger → convertir → écrire."""

    # 1. Télécharger les données quran-align
    raw_data = download_quran_align_data()

    # 2. Indexer par (surah, ayah)
    align_index = {}
    for entry in raw_data:
        key = (entry["surah"], entry["ayah"])
        align_index[key] = entry["segments"]

    print(f"   {len(align_index)} versets dans les données quran-align.")

    # 3. Charger le JSON enrichi
    enriched = load_enriched_json()

    # 4. Mettre à jour chaque verset
    updated = 0
    unchanged = 0
    missing = 0
    errors = []

    for surah_data in enriched:
        sn = surah_data["surah_number"]
        if sn not in JUZ_AMMA_RANGE:
            continue

        for verse in surah_data["verses"]:
            vn = verse["number"]
            words = verse.get("words", [])
            word_count = len(words)
            key = (sn, vn)

            if key not in align_index:
                missing += 1
                continue

            segments = align_index[key]
            new_timing = convert_segments_to_timings(segments, word_count)

            if not new_timing:
                errors.append(f"{sn}:{vn} — conversion vide")
                continue

            # Vérifier que le nombre de timings = nombre de mots
            if len(new_timing) != word_count:
                errors.append(
                    f"{sn}:{vn} — {len(new_timing)} timings ≠ {word_count} mots"
                )
                continue

            old_timing = verse.get("audio_timing", [])

            if new_timing != old_timing:
                if dry_run:
                    print(f"  📝 {sn}:{vn} ({word_count} mots)")
                    print(f"     OLD = {old_timing}")
                    print(f"     NEW = {new_timing}")
                verse["audio_timing"] = new_timing
                updated += 1
            else:
                unchanged += 1

    # 5. Résumé
    print(f"\n{'═' * 50}")
    print(f"📊 Résultat :")
    print(f"   ✅ Mis à jour : {updated} versets")
    print(f"   ⏭️  Inchangés  : {unchanged} versets")
    print(f"   ⚠️  Manquants  : {missing} versets (pas dans quran-align)")
    if errors:
        print(f"   ❌ Erreurs    : {len(errors)}")
        for e in errors:
            print(f"      {e}")
    print(f"{'═' * 50}")

    # 6. Sauvegarder
    if not dry_run and updated > 0:
        save_enriched_json(enriched)
    elif dry_run:
        print("   (dry-run — aucune modification écrite)")
    else:
        print("   Aucune modification nécessaire.")


def main():
    parser = argparse.ArgumentParser(
        description="Injecte les vrais timestamps Husary dans juz_amma_enriched.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les changements sans écrire",
    )
    args = parser.parse_args()

    print("🕌 Génération des timestamps audio (quran-align / Husary)")
    print(f"   Fichier cible : {ENRICHED_JSON}")
    print()

    process_timings(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
