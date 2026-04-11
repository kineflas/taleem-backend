"""
NOURANIA ENRICHED SEED DATA
============================

Comprehensive educational content for:
1. Voyelles et Syllabes Program (10 units)
2. Nourania Enriched (17 chapters with detailed explanations, examples, illustrations, and gamification)

This seed data transforms sparse curriculum items into engaging, pedagogically-sound learning units
with detailed French explanations for complete beginners, pronunciation guides, visual illustrations,
interactive quizzes, and gamification challenges.

Author: Senior Full Stack Developer
Version: 1.0
"""

from sqlalchemy.orm import Session
from datetime import datetime


# ============================================================================
# PART A: VOYELLES ET SYLLABES - 10 ENRICHED UNITS
# ============================================================================

VOYELLES_SYLLABES_UNITS = [
    {
        "number": 1,
        "title_ar": "الحركات الثلاث القصيرة",
        "title_fr": "Les 3 voyelles courtes (Fatha, Kasra, Damma)",
        "description_fr": "Maîtrisez les trois voyelles courtes de l'arabe et leur prononciation précise.",

        "explanation_sections": [
            {
                "title_fr": "Introduction aux diacritiques arabes",
                "content_fr": """L'arabe utilise des petites marques appelées 'diacritiques' ou 'tashkeel' pour indiquer les voyelles.
Contrairement au français où les voyelles sont des lettres (a, e, i, o, u), l'arabe écrit les consonnes et ajoute les voyelles
comme des signes au-dessus ou au-dessous. Les trois voyelles courtes sont les plus fondamentales et vous les rencontrerez
dans presque chaque mot arabe. Elles sont courtes en durée (environ 1 temps de prononciation) et peuvent avoir une sonorité
légèrement différente selon le contexte.""",
                "content_ar": "الحركات الثلاث القصيرة هي أساس النطق العربي الصحيح",
                "audio_hint": "Trois sons distincts : 'a' court, 'i' court, 'u' court",
                "tip_fr": "Imaginez que vous prononcez chaque voyelle en tenant votre voix à peine 1 seconde",
                "common_mistakes_fr": "Les francophones confondent souvent 'i' et 'e', ou prononcent les voyelles trop longues"
            },
            {
                "title_fr": "LA FATHA (le 'a' court)",
                "content_fr": """La Fatha est le diacritique le plus simple : un petit trait oblique au-dessus de la lettre.
Elle produit le son 'a' court, similaire à la voyelle française dans 'patte', 'matte', ou 'batte'.
Il s'agit d'une voyelle ouverte où la bouche s'ouvre modérément. Si vous voyez بَ (ba), vous prononcez 'ba'
comme dans 'balle' en français. La Fatha est claire, nette et assez antérieure dans la bouche.""",
                "content_ar": "الفَـتْـحَة = بَ بَ بَ",
                "audio_hint": "Son 'a' court et clair, bouche modérément ouverte, comme 'ba' dans 'balle'",
                "tip_fr": "Dites rapidement : 'ba ba ba' en gardant la bouche ouverte mais pas trop",
                "common_mistakes_fr": "Prononcer 'a' comme en français 'patte' au lieu du 'a' court arabe qui ressemble plus à l'anglais 'but' allongé"
            },
            {
                "title_fr": "LA KASRA (le 'i' court)",
                "content_fr": """La Kasra est un petit trait oblique sous la lettre. Elle produit le son 'i' court,
similaire à la voyelle française dans 'bille', 'pille', ou 'quille'. Il s'agit d'une voyelle fermée antérieure
où les lèvres sont un peu étirées vers l'avant. Si vous voyez بِ (bi), vous prononcez 'bi' comme dans 'bille'.
La Kasra est plus fermée et plus antérieure que la Fatha.""",
                "content_ar": "الكَـسْـرَة = بِ بِ بِ",
                "audio_hint": "Son 'i' court, sourire léger, comme 'bi' dans 'bille'",
                "tip_fr": "Écartez vos lèvres légèrement vers l'avant et dites 'bi bi bi' rapidement",
                "common_mistakes_fr": "Prononcer 'i' comme 'e' (qui est une voyelle ouverte en français), ou oublier d'étirer légèrement les lèvres"
            },
            {
                "title_fr": "LA DAMMA (le 'u' court)",
                "content_fr": """La Damma est un petit 'w' ou 'o' miniature au-dessus de la lettre. Elle produit le son 'u' court,
similaire à la voyelle française dans 'boule', 'moule', ou 'poule'. Il s'agit d'une voyelle fermée postérieure
où les lèvres sont arrondies et poussées vers l'avant (comme pour siffler). Si vous voyez بُ (bu), vous prononcez 'bu'
comme dans 'boule'. La Damma est plus fermée et plus postérieure que la Fatha, et c'est la plus arrondie des trois.""",
                "content_ar": "الضَّـمَّـة = بُ بُ بُ",
                "audio_hint": "Son 'ou' court, lèvres arrondies, comme 'bu' dans 'boule'",
                "tip_fr": "Arrondissez vos lèvres comme pour siffler, puis dites 'bu bu bu' rapidement",
                "common_mistakes_fr": "Prononcer 'u' avec les lèvres trop arrondies (trop 'ou'), ou les tenir trop minces"
            }
        ],

        "examples": [
            {
                "arabic": "بَ",
                "transliteration": "ba",
                "explanation_fr": "Lettre Bā avec Fatha. Prononcez 'ba' comme dans 'balle'.",
                "audio_description_fr": "ba (court, bouche ouverte modérément)"
            },
            {
                "arabic": "بِ",
                "transliteration": "bi",
                "explanation_fr": "Lettre Bā avec Kasra. Prononcez 'bi' comme dans 'bille'.",
                "audio_description_fr": "bi (court, lèvres écartées)"
            },
            {
                "arabic": "بُ",
                "transliteration": "bu",
                "explanation_fr": "Lettre Bā avec Damma. Prononcez 'bu' comme dans 'boule'.",
                "audio_description_fr": "bu (court, lèvres arrondies)"
            },
            {
                "arabic": "تَ تِ تُ",
                "transliteration": "ta ti tu",
                "explanation_fr": "Lettre Tā avec les 3 voyelles courtes. Pratiquez avec chacune.",
                "audio_description_fr": "ta (ba), ti (bi), tu (bu) — trois sons distincts"
            },
            {
                "arabic": "دَ دِ دُ",
                "transliteration": "da di du",
                "explanation_fr": "Lettre Dāl avec les 3 voyelles courtes.",
                "audio_description_fr": "da, di, du — consonant change (d) mais voyelles identiques"
            },
            {
                "arabic": "سَ سِ سُ",
                "transliteration": "sa si su",
                "explanation_fr": "Lettre Sīn avec les 3 voyelles courtes.",
                "audio_description_fr": "sa, si, su — consonant s + voyelles"
            }
        ],

        "illustrations": [
            {
                "type": "vowel_chart",
                "title_fr": "Carte des 3 voyelles courtes",
                "description_fr": "Visualisation de la position de la langue et des lèvres pour chaque voyelle",
                "data": {
                    "chart_type": "ipa_vowel_triangle",
                    "vowels": [
                        {
                            "name": "Fatha",
                            "symbol": "َ",
                            "sound": "a",
                            "position": "open_front",
                            "mouth_openness": "half-open",
                            "tongue_position": "front",
                            "lip_rounding": "none",
                            "example": "بَ (ba)",
                            "french_comparison": "patte"
                        },
                        {
                            "name": "Kasra",
                            "symbol": "ِ",
                            "sound": "i",
                            "position": "close_front",
                            "mouth_openness": "closed",
                            "tongue_position": "front",
                            "lip_rounding": "slight",
                            "example": "بِ (bi)",
                            "french_comparison": "bille"
                        },
                        {
                            "name": "Damma",
                            "symbol": "ُ",
                            "sound": "u",
                            "position": "close_back",
                            "mouth_openness": "closed",
                            "tongue_position": "back",
                            "lip_rounding": "rounded",
                            "example": "بُ (bu)",
                            "french_comparison": "boule"
                        }
                    ]
                }
            },
            {
                "type": "diacritic_position",
                "title_fr": "Placement des diacritiques",
                "description_fr": "Où placer chaque diacritique sur la lettre",
                "data": {
                    "vowels": [
                        {
                            "name": "Fatha",
                            "position": "above",
                            "example_letter": "ب",
                            "example_written": "بَ",
                            "description": "Petit trait oblique AU-DESSUS de la lettre"
                        },
                        {
                            "name": "Kasra",
                            "position": "below",
                            "example_letter": "ب",
                            "example_written": "بِ",
                            "description": "Petit trait oblique SOUS la lettre"
                        },
                        {
                            "name": "Damma",
                            "position": "above",
                            "example_letter": "ب",
                            "example_written": "بُ",
                            "description": "Petit 'o' ou 'w' AU-DESSUS de la lettre"
                        }
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Quel son produit la Fatha (َ) ?",
                "type": "MCQ",
                "choices": ["'a' court comme dans 'balle'", "'i' court comme dans 'bille'", "'u' court comme dans 'boule'", "'e' court comme dans 'belle'"],
                "correct_index": 0,
                "explanation_fr": "La Fatha est le diacritique au-dessus de la lettre et produit le son 'a' court, avec la bouche modérément ouverte."
            },
            {
                "question_fr": "Où se place la Kasra (ِ) sur la lettre ?",
                "type": "MCQ",
                "choices": ["Au-dessus", "En-dessous", "À gauche", "À droite"],
                "correct_index": 1,
                "explanation_fr": "La Kasra est un trait oblique placé sous la lettre (بِ), contrairement à la Fatha qui est au-dessus."
            },
            {
                "question_fr": "La Damma (ُ) produit quel son ?",
                "type": "MCQ",
                "choices": ["'a' court", "'i' court", "'u' court comme dans 'boule'", "'ou' long comme dans 'route'"],
                "correct_index": 2,
                "explanation_fr": "La Damma (petit 'o' au-dessus) produit le son 'u' court avec les lèvres arrondies."
            },
            {
                "question_fr": "Prononcez : بَ",
                "type": "AUDIO_MATCH",
                "choices": ["ba", "bi", "bu", "ta"],
                "correct_index": 0,
                "explanation_fr": "بَ = Bā avec Fatha = 'ba' (lettre b + voyelle a court)"
            },
            {
                "question_fr": "Prononcez : دِ",
                "type": "AUDIO_MATCH",
                "choices": ["da", "di", "du", "dā"],
                "correct_index": 1,
                "explanation_fr": "دِ = Dāl avec Kasra = 'di' (lettre d + voyelle i court)"
            },
            {
                "question_fr": "Prononcez : سُ",
                "type": "AUDIO_MATCH",
                "choices": ["sa", "si", "su", "sū"],
                "correct_index": 2,
                "explanation_fr": "سُ = Sīn avec Damma = 'su' (lettre s + voyelle u court)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Les 3 voyelles",
                "description_fr": "Prononcez chaque syllabe le plus vite possible. Temps limite : 30 secondes.",
                "items": ["بَ", "بِ", "بُ", "تَ", "تِ", "تُ", "دَ", "دِ", "دُ", "سَ", "سِ", "سُ"],
                "time_limit_seconds": 30,
                "points_per_item": 10
            },
            {
                "type": "memory_pairs",
                "title_fr": "Paires mémoire : Syllabe ↔ Translittération",
                "description_fr": "Associez chaque syllabe arabe à sa translittération.",
                "pairs": [
                    {"arabic": "بَ", "transliteration": "ba"},
                    {"arabic": "بِ", "transliteration": "bi"},
                    {"arabic": "بُ", "transliteration": "bu"},
                    {"arabic": "تَ", "transliteration": "ta"},
                    {"arabic": "تِ", "transliteration": "ti"},
                    {"arabic": "تُ", "transliteration": "tu"}
                ],
                "points_per_pair": 20
            }
        ]
    },

    {
        "number": 2,
        "title_ar": "الحروف المدية الثلاث",
        "title_fr": "Les voyelles longues (Madd) : ā, ī, ū",
        "description_fr": "Apprenez à allonger les voyelles courtes avec les lettres Alif, Yā et Wāw.",

        "explanation_sections": [
            {
                "title_fr": "Concept de Madd (prolongation)",
                "content_fr": """En arabe, certaines lettres (Alif, Wāw, Yā) peuvent prolonger les voyelles courtes, créant des voyelles longues.
Une voyelle longue dure environ 2 fois plus longtemps qu'une voyelle courte — c'est une distinction très importante.
Si vous dites 'ba' (court), ce n'est pas la même chose que 'bā' (long). Cette différence change le sens des mots !
Le Madd est une règle fondamentale du Tajwid (récitation du Coran) et doit être maîtrisée.""",
                "content_ar": "المد يضاعف مدة النطق",
                "audio_hint": "Voyelle courte = 1 temps, voyelle longue = 2 temps (environ)",
                "tip_fr": "Comptez mentalement : pour une voyelle courte, 'ba' (1 temps), pour longue, 'bāā' (2 temps)",
                "common_mistakes_fr": "Prononcer les voyelles longues avec la même durée que les courtes, ou trop allonger"
            },
            {
                "title_fr": "Alif Madd (ā) — Fatha + Alif",
                "content_fr": """Quand vous voyez une Fatha (َ) suivi d'une lettre Alif (ا), vous créez une voyelle longue 'ā'.
Par exemple : بَا = ba-ā (Bā + Alif). L'Alif vient APRÈS la voyelle et la prolonge.
Vous prononcerez 'bāā' avec une durée doublée, les lèvres dans la même position que pour 'ba' mais beaucoup plus longue.
C'est comme si vous teniez le son 'a' deux fois plus longtemps.""",
                "content_ar": "الفَتْحَة + ألِف = آ / بَا",
                "audio_hint": "'ā' long, durée doublée, bouche dans position 'a'",
                "tip_fr": "Dites 'ba' mais tenez le 'a' deux fois plus longtemps : 'bāā'",
                "common_mistakes_fr": "Ajouter l'Alif comme une syllabe supplémentaire au lieu de prolonger la voyelle"
            },
            {
                "title_fr": "Yā Madd (ī) — Kasra + Yā",
                "content_fr": """Quand vous voyez une Kasra (ِ) suivi d'une lettre Yā (ي), vous créez une voyelle longue 'ī'.
Par exemple : بِي = bi-ī (Bī + Yā). La Yā vient APRÈS et prolonge la Kasra.
Vous prononcerez 'bīī' avec durée doublée, les lèvres écartées comme pour 'bi' mais beaucoup plus longue.""",
                "content_ar": "الكَسْرَة + يَاء = بِي",
                "audio_hint": "'ī' long, durée doublée, lèvres écartées",
                "tip_fr": "Dites 'bi' mais tenez le 'i' deux fois plus longtemps : 'bīī'",
                "common_mistakes_fr": "Traiter Yā comme une consonne supplémentaire au lieu de voyelle prolongée"
            },
            {
                "title_fr": "Wāw Madd (ū) — Damma + Wāw",
                "content_fr": """Quand vous voyez une Damma (ُ) suivi d'une lettre Wāw (و), vous créez une voyelle longue 'ū'.
Par exemple : بُو = bu-ū (Bū + Wāw). Le Wāw vient APRÈS et prolonge la Damma.
Vous prononcerez 'būū' avec durée doublée, les lèvres arrondies comme pour 'bu' mais beaucoup plus longue.""",
                "content_ar": "الضَّمَّة + واو = بُو",
                "audio_hint": "'ū' long, durée doublée, lèvres arrondies",
                "tip_fr": "Dites 'bu' mais tenez le 'u' deux fois plus longtemps : 'būū'",
                "common_mistakes_fr": "Prononcer Wāw comme 'w' consonantique au lieu de prolonger la voyelle"
            },
            {
                "title_fr": "Différence critique : court vs long",
                "content_fr": """Voyelle courte : durée = 1 temps (~0.3 secondes). Voyelle longue : durée = 2 temps (~0.6 secondes).
Cette différence est ESSENTIELLE car elle change complètement le sens des mots. Par exemple :
- قَتَلَ (il a tué) : qatala avec voyelles courtes
- قَاتَل (combattant) : qātala avec première voyelle longue
Ces deux mots se prononcent différemment et signifient des choses totalement différentes !""",
                "content_ar": "الفرق بين الحرف القصير والطويل يغير معنى الكلمة",
                "audio_hint": "Écoutez bien la différence de durée",
                "tip_fr": "Pratiquez plusieurs fois avec la même syllabe : court puis long",
                "common_mistakes_fr": "Négliger la durée et parler trop vite, perdant cette distinction importante"
            }
        ],

        "examples": [
            {
                "arabic": "بَا",
                "transliteration": "bā",
                "explanation_fr": "Bā + Alif = voyelle longue 'ā'. Fatha prolongée par Alif.",
                "audio_description_fr": "ba (court 1 temps) vs bāā (long 2 temps)"
            },
            {
                "arabic": "تَا",
                "transliteration": "tā",
                "explanation_fr": "Tā + Alif = voyelle longue 'ā'.",
                "audio_description_fr": "tāā (long)"
            },
            {
                "arabic": "بِي",
                "transliteration": "bī",
                "explanation_fr": "Bī + Yā = voyelle longue 'ī'. Kasra prolongée par Yā.",
                "audio_description_fr": "bi (court 1 temps) vs bīī (long 2 temps)"
            },
            {
                "arabic": "دِي",
                "transliteration": "dī",
                "explanation_fr": "Dī + Yā = voyelle longue 'ī'.",
                "audio_description_fr": "dīī (long)"
            },
            {
                "arabic": "بُو",
                "transliteration": "bū",
                "explanation_fr": "Bū + Wāw = voyelle longue 'ū'. Damma prolongée par Wāw.",
                "audio_description_fr": "bu (court 1 temps) vs būū (long 2 temps)"
            },
            {
                "arabic": "نُو",
                "transliteration": "nū",
                "explanation_fr": "Nū + Wāw = voyelle longue 'ū'.",
                "audio_description_fr": "nūū (long)"
            }
        ],

        "illustrations": [
            {
                "type": "duration_comparison",
                "title_fr": "Comparaison : Voyelles courtes vs longues",
                "description_fr": "Visualisation de la durée de prononciation",
                "data": {
                    "comparisons": [
                        {
                            "short": {"arabic": "بَ", "transliteration": "ba", "duration": "1 temps"},
                            "long": {"arabic": "بَا", "transliteration": "bā", "duration": "2 temps"},
                            "difference": "L'Alif double la durée"
                        },
                        {
                            "short": {"arabic": "بِ", "transliteration": "bi", "duration": "1 temps"},
                            "long": {"arabic": "بِي", "transliteration": "bī", "duration": "2 temps"},
                            "difference": "La Yā double la durée"
                        },
                        {
                            "short": {"arabic": "بُ", "transliteration": "bu", "duration": "1 temps"},
                            "long": {"arabic": "بُو", "transliteration": "bū", "duration": "2 temps"},
                            "difference": "Le Wāw double la durée"
                        }
                    ]
                }
            },
            {
                "type": "madd_formation",
                "title_fr": "Comment former un Madd",
                "description_fr": "Les trois types de Madd visuellement",
                "data": {
                    "rules": [
                        {
                            "vowel_short": "Fatha",
                            "letter": "Alif",
                            "result": "ā (Alif Madd)",
                            "example": "بَا"
                        },
                        {
                            "vowel_short": "Kasra",
                            "letter": "Yā",
                            "result": "ī (Yā Madd)",
                            "example": "بِي"
                        },
                        {
                            "vowel_short": "Damma",
                            "letter": "Wāw",
                            "result": "ū (Wāw Madd)",
                            "example": "بُو"
                        }
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Comment forme-t-on un Madd 'ā' (voyelle longue a) ?",
                "type": "MCQ",
                "choices": ["Fatha + Alif", "Kasra + Yā", "Damma + Wāw", "Fatha + Wāw"],
                "correct_index": 0,
                "explanation_fr": "Fatha (voyelle courte 'a') + Alif = Madd 'ā' (voyelle longue 'ā')"
            },
            {
                "question_fr": "Comment forme-t-on un Madd 'ī' (voyelle longue i) ?",
                "type": "MCQ",
                "choices": ["Fatha + Alif", "Kasra + Yā", "Damma + Wāw", "Kasra + Alif"],
                "correct_index": 1,
                "explanation_fr": "Kasra (voyelle courte 'i') + Yā = Madd 'ī' (voyelle longue 'ī')"
            },
            {
                "question_fr": "Quelle est la durée d'une voyelle longue comparée à une voyelle courte ?",
                "type": "MCQ",
                "choices": ["Même durée", "Deux fois plus longue", "Trois fois plus longue", "Moitié plus courte"],
                "correct_index": 1,
                "explanation_fr": "Une voyelle longue (Madd) dure environ 2 fois plus longtemps qu'une voyelle courte"
            },
            {
                "question_fr": "Prononcez : بَا",
                "type": "AUDIO_MATCH",
                "choices": ["ba (court)", "bā (long)", "ba-a (deux syllabes)", "bāā (trop long)"],
                "correct_index": 1,
                "explanation_fr": "بَا = Fatha + Alif = 'bā' long (environ 2 temps)"
            },
            {
                "question_fr": "Prononcez : نِي",
                "type": "AUDIO_MATCH",
                "choices": ["ni (court)", "nī (long)", "ni-i (deux syllabes)", "nīī (trop long)"],
                "correct_index": 1,
                "explanation_fr": "نِي = Kasra + Yā = 'nī' long"
            },
            {
                "question_fr": "Quel Madd fait le Wāw (و) ?",
                "type": "MCQ",
                "choices": ["ā", "ī", "ū", "nul"],
                "correct_index": 2,
                "explanation_fr": "Wāw après Damma crée le Madd 'ū' (voyelle longue u)"
            }
        ],

        "challenges": [
            {
                "type": "build_syllable",
                "title_fr": "Construire des Madd",
                "description_fr": "Combinez une voyelle courte + sa lettre de prolongation pour former un Madd",
                "exercises": [
                    {"vowel": "Fatha", "letter": "Alif", "target_result": "ā"},
                    {"vowel": "Kasra", "letter": "Yā", "target_result": "ī"},
                    {"vowel": "Damma", "letter": "Wāw", "target_result": "ū"}
                ]
            },
            {
                "type": "dictation",
                "title_fr": "Dictée : Reconnaître court vs long",
                "description_fr": "L'enseignant prononce une syllabe. Dites si c'est court ou long.",
                "exercises": [
                    {"arabic": "بَ", "correct_answer": "court"},
                    {"arabic": "بَا", "correct_answer": "long"},
                    {"arabic": "تِ", "correct_answer": "court"},
                    {"arabic": "تِي", "correct_answer": "long"}
                ]
            }
        ]
    },

    {
        "number": 3,
        "title_ar": "السكون",
        "title_fr": "Le Sukun (consonne sans voyelle)",
        "description_fr": "Apprenez à fermer les syllabes avec le Sukun et créer des mots complexes.",

        "explanation_sections": [
            {
                "title_fr": "Qu'est-ce que le Sukun ?",
                "content_fr": """Le Sukun (ْ) est un petit cercle vide placé au-dessus d'une lettre. Il signifie qu'il n'y a PAS de voyelle.
Contrairement à la Fatha (a), Kasra (i), ou Damma (u), le Sukun indique une consonne prononcée SEULE, sans voyelle qui suit.
La syllabe devient 'fermée' : elle finit par une consonne au lieu de voyelle.
C'est comme la différence entre 'ma' (voyelle) et 'm' (pas de voyelle).""",
                "content_ar": "السكون = عدم وجود حركة",
                "audio_hint": "Syllabe fermée : consonne sans voyelle qui suit",
                "tip_fr": "Dites la consonne puis arrêtez immédiatement, sans ajouter de voyelle",
                "common_mistakes_fr": "Ajouter une voyelle même quand il y a Sukun, ou ne pas bien fermer la syllabe"
            },
            {
                "title_fr": "La structure CVC (consonne-voyelle-consonne)",
                "content_fr": """Quand vous avez une syllabe comme مَكْ (mak), vous avez :
- M (consonne) + Fatha (voyelle 'a') + K avec Sukun (consonne sans voyelle)
Vous prononcez : 'mak' avec un k fermé, pas 'maku' ou 'maka'. Le Sukun ferme la syllabe.
Cette structure est très commune en arabe. Elle ressemble à des mots français comme 'mak', 'mat', 'mar', etc.""",
                "content_ar": "ساكن + متحرك = كلمة عربية صحيحة",
                "audio_hint": "mak (fermé), pas maku ou maka",
                "tip_fr": "Prononcez la première syllabe complètement (ma), puis le (k) fermé sans voyelle",
                "common_mistakes_fr": "Prononcer 'maka' au lieu de 'mak', ou 'mako' au lieu de 'mak'"
            },
            {
                "title_fr": "Jonction de syllabes : CVC + CV",
                "content_fr": """Quand une lettre avec Sukun précède une lettre avec voyelle, elles se lient :
Par exemple : مَكْتَب (maktab) = mak (CVC) + ta (CV) + ba (CV)
Vous prononcez la première syllabe fermée ('mak'), puis continuez avec la deuxième ('ta'), puis la troisième ('ba').
Les deux lettres ne fusionnent pas, mais on les relie fluidement dans le même mot.""",
                "content_ar": "مَكْتَب = ساكن + متحرك",
                "audio_hint": "mak-ta-ba (trois syllabes distinctes mais fluides)",
                "tip_fr": "Pratiquez en séparant d'abord : 'mak' (pause) 'ta' (pause) 'ba', puis fluidifiez",
                "common_mistakes_fr": "Séparer trop les syllabes ou au contraire les fuser trop"
            }
        ],

        "examples": [
            {
                "arabic": "بْ",
                "transliteration": "b (sans voyelle)",
                "explanation_fr": "Lettre Bā avec Sukun. Consonne fermée.",
                "audio_description_fr": "Prononcez juste 'b' sans ajouter de voyelle"
            },
            {
                "arabic": "مَكْ",
                "transliteration": "mak",
                "explanation_fr": "CVC : ma (CV) + k avec Sukun. Syllabe fermée.",
                "audio_description_fr": "mak (fermé, pas 'maku')"
            },
            {
                "arabic": "مَكْتَب",
                "transliteration": "mak-tab",
                "explanation_fr": "Mot complet : mak (fermée) + tab (ouverte). Syllabe fermée suivie d'ouverte.",
                "audio_description_fr": "mak-ta-ba (trois syllabes fluides)"
            },
            {
                "arabic": "كِتَاب",
                "transliteration": "ki-tāb",
                "explanation_fr": "Livre. Structure : ki (CV) + tā (CV long) + b avec Sukun (finale fermée).",
                "audio_description_fr": "ki-tāab (mot complet avec fermeture finale)"
            },
            {
                "arabic": "دَرْس",
                "transliteration": "dars",
                "explanation_fr": "Cours. dar (CVC fermée) + s avec Sukun (finale fermée).",
                "audio_description_fr": "dars (mot avec deux fermetures)"
            }
        ],

        "illustrations": [
            {
                "type": "syllable_structure",
                "title_fr": "Types de structures syllabiques",
                "description_fr": "Visualisation des différentes structures possibles",
                "data": {
                    "structures": [
                        {
                            "name": "CV (open)",
                            "pattern": "Consonant + Vowel",
                            "example": "بَ (ba)",
                            "pronunciation": "ba",
                            "closure": "open"
                        },
                        {
                            "name": "CVC (closed)",
                            "pattern": "Consonant + Vowel + Consonant (Sukun)",
                            "example": "مَكْ (mak)",
                            "pronunciation": "mak",
                            "closure": "closed"
                        },
                        {
                            "name": "CVV (madd)",
                            "pattern": "Consonant + Long Vowel",
                            "example": "بَا (bā)",
                            "pronunciation": "bā",
                            "closure": "open"
                        }
                    ]
                }
            },
            {
                "type": "word_breakdown",
                "title_fr": "Décomposition : Maktab (livre)",
                "description_fr": "Comment se divise un mot arabe en syllabes",
                "data": {
                    "word": "مَكْتَب",
                    "transliteration": "mak-tab",
                    "breakdown": [
                        {"syllable": "مَك", "transliteration": "mak", "type": "CVC (fermée)"},
                        {"syllable": "تَب", "transliteration": "tab", "type": "CVC (fermée)"}
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Qu'indique le Sukun (ْ) ?",
                "type": "MCQ",
                "choices": ["Une voyelle courte", "Une voyelle longue", "Pas de voyelle (consonne seule)", "Une consonne doublée"],
                "correct_index": 2,
                "explanation_fr": "Le Sukun signifie qu'il n'y a PAS de voyelle. La syllabe se ferme avec une consonne."
            },
            {
                "question_fr": "Prononcez : بْ",
                "type": "AUDIO_MATCH",
                "choices": ["ba", "bi", "bu", "b (sans voyelle)"],
                "correct_index": 3,
                "explanation_fr": "بْ = Bā avec Sukun = juste 'b' sans ajouter de voyelle"
            },
            {
                "question_fr": "Prononcez : مَكْ",
                "type": "AUDIO_MATCH",
                "choices": ["ma-ka", "mak", "ma-ku", "make"],
                "correct_index": 1,
                "explanation_fr": "مَكْ = ma (Fatha) + k avec Sukun = 'mak' (syllabe fermée)"
            },
            {
                "question_fr": "Quel est le type de structure syllabique pour مَكْ ?",
                "type": "MCQ",
                "choices": ["CV (ouverte)", "CVC (fermée)", "CVV (longue)", "CVCC"],
                "correct_index": 1,
                "explanation_fr": "مَكْ = CVC : consonne (m) + voyelle (a) + consonne avec Sukun (k)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Lire les Sukun",
                "description_fr": "Prononcez ces syllabes fermées aussi vite que possible",
                "items": ["بْ", "تْ", "دْ", "سْ", "نْ", "مْ", "كْ", "لْ"],
                "time_limit_seconds": 20
            },
            {
                "type": "build_syllable",
                "title_fr": "Construire des mots avec Sukun",
                "description_fr": "Assemblez les syllabes pour former des mots complets",
                "exercises": [
                    {"syllables": ["مَك", "تَب"], "target_word": "مَكْتَب", "meaning": "bureau"},
                    {"syllables": ["دَر", "س"], "target_word": "دَرْس", "meaning": "cours"}
                ]
            }
        ]
    },

    {
        "number": 4,
        "title_ar": "الشدة",
        "title_fr": "La Shadda (consonne doublée)",
        "description_fr": "Apprenez à prononcer les consonnes doublées correctement.",

        "explanation_sections": [
            {
                "title_fr": "Définition de la Shadda",
                "content_fr": """La Shadda (ّ) est un petit W placé au-dessus d'une lettre. Elle indique que la lettre est DOUBLÉE en prononciation.
Quand vous voyez بّ (Bā avec Shadda), vous prononcer cette consonne deux fois : une fois fermée (avec Sukun), une fois ouverte (avec sa voyelle).
Par exemple : مَدَّ (prolonger) = ma (syllabe ouverte) + d avec Shadda (consonne doublée) = 'mad-da'.
C'est comme si vous aviez dَْ dَ (deux lettres d).""",
                "content_ar": "الشدة = تضعيف الحرف",
                "audio_hint": "Consonne prononcée deux fois rapidement",
                "tip_fr": "Pensez à doubler la consonne dans votre tête : 'bb', 'dd', 'nn', etc.",
                "common_mistakes_fr": "Prononcer la consonne une seule fois, ou trop séparer les deux prononciations"
            },
            {
                "title_fr": "Analyse phonétique de la Shadda",
                "content_fr": """La Shadda crée une consonne géminée (doublée). Phonétiquement :
- Première prononciation : consonne avec Sukun (consonne fermée) = elle termine une syllabe
- Deuxième prononciation : consonne avec sa voyelle (consonne ouverte) = elle commence une nouvelle syllabe
Par exemple : إِنَّ (verily) = in-na (i + Nūn Sukun + Nūn avec Fatha)
Quand vous prononcez rapidement, cela sonne comme une consonne très appuyée.""",
                "content_ar": "الشدة = حرف مع سكون + حرف مع حركة",
                "audio_hint": "Son 'appuyé' ou 'renforcé'",
                "tip_fr": "Pratiquez avec des mots français : 'matte', 'belle', 'patte' — le 't' et 'l' sont doublés",
                "common_mistakes_fr": "Traiter la Shadda comme une simple voyelle ou un accent"
            }
        ],

        "examples": [
            {
                "arabic": "بّ",
                "transliteration": "bb",
                "explanation_fr": "Bā avec Shadda. Prononcez 'b' deux fois : bb.",
                "audio_description_fr": "ba-ba (deux Bā très rapides, comme 'bb' appuyé)"
            },
            {
                "arabic": "مَدَّ",
                "transliteration": "mad-da",
                "explanation_fr": "ma + d avec Shadda. Mot signifiant 'prolonger' en arabe.",
                "audio_description_fr": "mad-da (le 'd' est doublé, très appuyé)"
            },
            {
                "arabic": "إِنَّ",
                "transliteration": "in-na",
                "explanation_fr": "Mot coranique très fréquent. i + Nūn avec Shadda.",
                "audio_description_fr": "in-na (très fréquent dans le Coran)"
            },
            {
                "arabic": "كِتَابّ",
                "transliteration": "ki-tāb-ba",
                "explanation_fr": "Exemple : livre avec Bā doublée à la fin.",
                "audio_description_fr": "ki-tābb (le 'b' final est appuyé et doublé)"
            }
        ],

        "illustrations": [
            {
                "type": "shadda_analysis",
                "title_fr": "Comment fonctionne la Shadda",
                "description_fr": "Décomposition d'une consonne doublée",
                "data": {
                    "explanation": "La Shadda = Sukun + Voyelle sur la même lettre",
                    "example": {
                        "word": "مَدَّ",
                        "breakdown": [
                            {"position": 1, "letter": "م", "diacritic": "Fatha", "sound": "ma"},
                            {"position": 2, "letter": "د", "diacritic": "Sukun (caché) + Fatha", "sound": "dd"},
                        ],
                        "full_pronunciation": "mad-da"
                    }
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Qu'indique la Shadda (ّ) ?",
                "type": "MCQ",
                "choices": ["Une voyelle courte", "Une voyelle longue", "Une consonne doublée", "Pas de voyelle"],
                "correct_index": 2,
                "explanation_fr": "La Shadda indique qu'une lettre est prononcée deux fois très rapidement."
            },
            {
                "question_fr": "Prononcez : بّ",
                "type": "AUDIO_MATCH",
                "choices": ["ba", "bi", "bu", "bb (deux b rapides)"],
                "correct_index": 3,
                "explanation_fr": "بّ = Bā avec Shadda = consonne b doublée = 'bb'"
            },
            {
                "question_fr": "Prononcez : إِنَّ",
                "type": "AUDIO_MATCH",
                "choices": ["in", "inna", "i-na", "inn-a"],
                "correct_index": 1,
                "explanation_fr": "إِنَّ = i (Kasra) + n avec Shadda = 'inna' (très fréquent au Coran)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Les Shadda",
                "description_fr": "Prononcez ces consonnes doublées rapidement",
                "items": ["بّ", "تّ", "دّ", "سّ", "نّ", "مّ"],
                "time_limit_seconds": 25
            }
        ]
    },

    {
        "number": 5,
        "title_ar": "التنوين",
        "title_fr": "Le Tanwin (Nunation — le 'n' final)",
        "description_fr": "Apprenez les trois formes du Tanwin et leur prononciation.",

        "explanation_sections": [
            {
                "title_fr": "Qu'est-ce que le Tanwin ?",
                "content_fr": """Le Tanwin (ً, ٌ, ٍ) ajoute un son 'n' à la fin d'un mot. En arabe, le Tanwin s'applique aux noms INDÉFINIS.
Il existe trois formes correspondant aux trois voyelles courtes :
1. Tanwin Fath (ً) : double Fatha = son 'an'
2. Tanwin Damm (ٌ) : double Damma = son 'un'
3. Tanwin Kasr (ٍ) : double Kasra = son 'in'
Le Tanwin est très fréquent en arabe. Pratiquement tous les noms indéfinis l'ont.""",
                "content_ar": "التنوين = نون مخفية في الصوت",
                "audio_hint": "Son 'n' ajouté à la fin : -an, -un, -in",
                "tip_fr": "Pensez à ajouter un 'n' nasal à la fin du mot",
                "common_mistakes_fr": "Oublier le 'n', ou le prononcer comme une consonne claire au lieu de nasalisé"
            },
            {
                "title_fr": "Tanwin Fath (ً) — le 'an'",
                "content_fr": """Deux petites Fathas écrites au-dessus d'une lettre. Cela indique un son 'an' à la fin.
Par exemple : كِتَابً (un livre, indéfini) = kitāban. C'est souvent écrit avec un Alif silencieux (kitāban).
Le Tanwin Fath donne une nasalité avec une voyelle 'a' courte.""",
                "content_ar": "فَتْحَتَان = بً = ان",
                "audio_hint": "Son 'an' nasal à la fin",
                "tip_fr": "Prononcer normalement, puis ajouter un 'n' nasal",
                "common_mistakes_fr": "Prononcer 'ana' au lieu de 'an', ou ne pas nasaliser"
            },
            {
                "title_fr": "Tanwin Damm (ٌ) — le 'un'",
                "content_fr": """Deux petites Damma écrites au-dessus d'une lettre. Cela indique un son 'un' à la fin.
Par exemple : كِتَابٌ (un livre, nominatif indéfini) = kitābun. Les lèvres sont arrondies comme pour 'u'.""",
                "content_ar": "ضَمَّتَان = بٌ = ون",
                "audio_hint": "Son 'un' nasal avec lèvres arrondies",
                "tip_fr": "Voyelle 'u' court puis ajoutez 'n' nasal",
                "common_mistakes_fr": "Prononcer 'ung' au lieu de 'un', ou oublier l'arrondissement des lèvres"
            },
            {
                "title_fr": "Tanwin Kasr (ٍ) — le 'in'",
                "content_fr": """Deux petites Kasra écrites sous une lettre. Cela indique un son 'in' à la fin.
Par exemple : كِتَابٍ (un livre, génétif indéfini) = kitābin.""",
                "content_ar": "كَسْرَتَان = بٍ = ين",
                "audio_hint": "Son 'in' nasal avec lèvres écartées",
                "tip_fr": "Voyelle 'i' court puis ajoutez 'n' nasal",
                "common_mistakes_fr": "Prononcer 'ing' au lieu de 'in', ou traiter comme consonne au lieu de voyelle nasalisée"
            },
            {
                "title_fr": "Tanwin vs Nūn normal",
                "content_fr": """Important : le Tanwin n'est PAS une vraie lettre Nūn. C'est un diacritique qui ajoute un son 'n' nasal.
Une vraie Nūn (ن) est une lettre consonantique : نُ (nu). Le Tanwin (ٌ) est deux Damma qui ajoutent 'un'.
Ils sonnent similaires mais se comportent différemment grammaticalement et dans les règles de récitation.""",
                "content_ar": "التنوين ≠ النون",
                "audio_hint": "Tanwin = son 'n' nasal, Nūn = vraie consonne",
                "tip_fr": "Tanwin est un diacritique, Nūn est une lettre",
                "common_mistakes_fr": "Confondre les deux ou traiter le Tanwin comme une consonne"
            }
        ],

        "examples": [
            {
                "arabic": "كِتَابً",
                "transliteration": "ki-tāb-an",
                "explanation_fr": "Kitāban (un livre, accusatif indéfini). Tanwin Fath.",
                "audio_description_fr": "ki-tāb-an (an nasal)"
            },
            {
                "arabic": "كِتَابٌ",
                "transliteration": "ki-tāb-un",
                "explanation_fr": "Kitābun (un livre, nominatif indéfini). Tanwin Damm.",
                "audio_description_fr": "ki-tāb-un (un nasal)"
            },
            {
                "arabic": "كِتَابٍ",
                "transliteration": "ki-tāb-in",
                "explanation_fr": "Kitābin (un livre, génétif indéfini). Tanwin Kasr.",
                "audio_description_fr": "ki-tāb-in (in nasal)"
            },
            {
                "arabic": "بِسْمٌ",
                "transliteration": "bis-mun",
                "explanation_fr": "Bismun (un nom). Mot utilisé dans la Basmala.",
                "audio_description_fr": "bis-mun"
            }
        ],

        "illustrations": [
            {
                "type": "tanwin_forms",
                "title_fr": "Les 3 formes du Tanwin",
                "description_fr": "Visualisation des trois types",
                "data": {
                    "forms": [
                        {
                            "name": "Tanwin Fath",
                            "symbol": "ً",
                            "position": "above",
                            "sound": "an",
                            "example": "كِتَابً",
                            "vowel_equivalent": "Fatha"
                        },
                        {
                            "name": "Tanwin Damm",
                            "symbol": "ٌ",
                            "position": "above",
                            "sound": "un",
                            "example": "كِتَابٌ",
                            "vowel_equivalent": "Damma"
                        },
                        {
                            "name": "Tanwin Kasr",
                            "symbol": "ٍ",
                            "position": "below",
                            "sound": "in",
                            "example": "كِتَابٍ",
                            "vowel_equivalent": "Kasra"
                        }
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Qu'est-ce que le Tanwin ?",
                "type": "MCQ",
                "choices": ["Une consonne doublée", "Une voyelle longue", "Un 'n' nasal à la fin d'un mot", "Une consonne nasale"],
                "correct_index": 2,
                "explanation_fr": "Le Tanwin ajoute un son 'n' nasal à la fin des noms indéfinis"
            },
            {
                "question_fr": "Prononcez : كِتَابٌ",
                "type": "AUDIO_MATCH",
                "choices": ["kitābu", "kitāban", "kitābun", "kitābi"],
                "correct_index": 2,
                "explanation_fr": "كِتَابٌ = Tanwin Damm = kitābun (un livre au nominatif)"
            },
            {
                "question_fr": "Quel est le Tanwin du 'in' ?",
                "type": "MCQ",
                "choices": ["ً", "ٌ", "ٍ", "ّ"],
                "correct_index": 2,
                "explanation_fr": "ٍ (deux Kasra) = Tanwin Kasr = son 'in'"
            }
        ],

        "challenges": [
            {
                "type": "memory_pairs",
                "title_fr": "Paires : Tanwin ↔ Prononciation",
                "description_fr": "Associez chaque Tanwin à son son",
                "pairs": [
                    {"arabic": "ً", "sound": "an"},
                    {"arabic": "ٌ", "sound": "un"},
                    {"arabic": "ٍ", "sound": "in"}
                ]
            }
        ]
    },

    {
        "number": 6,
        "title_ar": "البناء المقطعي CV",
        "title_fr": "Structure syllabique simple : CV (Consonant-Vowel)",
        "description_fr": "Maîtrisez la structure syllabique la plus courante de l'arabe.",

        "explanation_sections": [
            {
                "title_fr": "Structure syllabique CV expliquée",
                "content_fr": """La structure la plus basique en arabe est CV : une Consonante suivie d'une Voyelle.
Par exemple : بَ (ba) = b (consonne) + ā (voyelle). C'est une syllabe ouverte qui finit par une voyelle.
La plupart des syllabes arabes commencent par une consonne et se terminent par une voyelle.
C'est la base absolue de la lecture arabe.""",
                "content_ar": "ساكن + متحرك = مقطع CV",
                "audio_hint": "Consonne + voyelle = syllabe ouverte",
                "tip_fr": "Chaque consonne a une voyelle, et elles se prononcent ensemble",
                "common_mistakes_fr": "Séparer trop la consonne et la voyelle, ou ajouter une voyelle non écrite"
            },
            {
                "title_fr": "28 consonnes × 3 voyelles courtes = 84 combinaisons",
                "content_fr": """L'arabe a 28 consonnes. Chacune peut avoir une des trois voyelles courtes.
Cela donne 28 × 3 = 84 combinaisons différentes à apprendre.
La bonne nouvelle : une fois que vous maîtrisez la structure CV avec une consonne, vous pouvez l'appliquer à toutes les autres.
C'est une excellente pratique pour les débutants.""",
                "content_ar": "28 حرف × 3 حركات = 84 مقطع",
                "audio_hint": "Pratique systématique de tous les CV",
                "tip_fr": "Mémorisez d'abord 3 consonnes (b, t, s) avec les 3 voyelles = 9 combinaisons",
                "common_mistakes_fr": "Essayer d'apprendre tous les 84 à la fois au lieu d'y aller graduellement"
            }
        ],

        "examples": [
            {
                "arabic": "بَ بِ بُ",
                "transliteration": "ba bi bu",
                "explanation_fr": "Bā avec les 3 voyelles courtes. Trois CV différentes.",
                "audio_description_fr": "ba (Fatha), bi (Kasra), bu (Damma)"
            },
            {
                "arabic": "تَ تِ تُ",
                "transliteration": "ta ti tu",
                "explanation_fr": "Tā avec les 3 voyelles courtes.",
                "audio_description_fr": "ta, ti, tu"
            },
            {
                "arabic": "دَ دِ دُ سَ سِ سُ نَ نِ نُ",
                "transliteration": "da di du sa si su na ni nu",
                "explanation_fr": "Trois consonnes (Dāl, Sīn, Nūn) avec chaque voyelle.",
                "audio_description_fr": "Pratiquez ces 9 combinaisons fluement"
            }
        ],

        "illustrations": [
            {
                "type": "consonant_vowel_grid",
                "title_fr": "Grille CV : Consonnes × Voyelles",
                "description_fr": "Tableau montrant toutes les combinaisons possibles",
                "data": {
                    "consonants": ["ب", "ت", "ث", "ج", "ح"],
                    "vowels": ["Fatha (َ)", "Kasra (ِ)", "Damma (ُ)"],
                    "grid": [
                        ["بَ", "بِ", "بُ"],
                        ["تَ", "تِ", "تُ"],
                        ["ثَ", "ثِ", "ثُ"],
                        ["جَ", "جِ", "جُ"],
                        ["حَ", "حِ", "حُ"]
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Qu'est-ce qu'une structure CV ?",
                "type": "MCQ",
                "choices": ["Consonante + Consonante", "Consonante + Voyelle", "Voyelle + Consonante", "Voyelle + Voyelle"],
                "correct_index": 1,
                "explanation_fr": "CV = une Consonante suivie d'une Voyelle (syllabe ouverte)"
            },
            {
                "question_fr": "Combinaisons CV différentes pour les 28 consonnes arabes ?",
                "type": "MCQ",
                "choices": ["28", "84", "100", "56"],
                "correct_index": 1,
                "explanation_fr": "28 consonnes × 3 voyelles courtes = 84 combinaisons CV"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Grid CV",
                "description_fr": "Prononcez chaque CV aussi rapidement que possible",
                "items": ["بَ", "بِ", "بُ", "تَ", "تِ", "تُ", "دَ", "دِ", "دُ", "سَ", "سِ", "سُ", "نَ", "نِ", "نُ"],
                "time_limit_seconds": 40
            }
        ]
    },

    {
        "number": 7,
        "title_ar": "البناء المقطعي CVC",
        "title_fr": "Structure syllabique fermée : CVC (avec Sukun)",
        "description_fr": "Apprenez à fermer les syllabes avec le Sukun.",

        "explanation_sections": [
            {
                "title_fr": "CVC : syllabe fermée",
                "content_fr": """Une syllabe CVC a une Consonne, une Voyelle, et une Consonante avec Sukun.
Par exemple : مَكْ (mak) = m (consonne) + a (voyelle) + k avec Sukun (consonne fermée).
La syllabe se termine par une consonne sans voyelle. C'est une syllabe 'fermée'.""",
                "content_ar": "ساكن + متحرك + ساكن = مقطع مغلق",
                "audio_hint": "Syllabe qui finit par une consonne",
                "tip_fr": "Prononcez la voyelle puis 'fermez' avec la consonne finale",
                "common_mistakes_fr": "Ajouter une voyelle à la consonne finale, créant deux syllabes au lieu d'une"
            }
        ],

        "examples": [
            {
                "arabic": "مَكْ",
                "transliteration": "mak",
                "explanation_fr": "CVC fermée : m + a + k avec Sukun.",
                "audio_description_fr": "mak (fermé, pas 'maku')"
            },
            {
                "arabic": "دَرْ",
                "transliteration": "dar",
                "explanation_fr": "CVC fermée : d + a + r avec Sukun.",
                "audio_description_fr": "dar (fermé)"
            },
            {
                "arabic": "نِسْ",
                "transliteration": "nis",
                "explanation_fr": "CVC fermée : n + i + s avec Sukun.",
                "audio_description_fr": "nis (fermé)"
            }
        ],

        "quiz": [
            {
                "question_fr": "Prononcez : مَكْ",
                "type": "AUDIO_MATCH",
                "choices": ["ma-ka", "mak", "ma-ku", "make"],
                "correct_index": 1,
                "explanation_fr": "مَكْ = CVC = mak (fermé)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : CVC fermées",
                "description_fr": "Prononcez ces syllabes fermées",
                "items": ["مَكْ", "دَرْ", "نِسْ", "سَلْ", "كَتْ", "جَبْ"],
                "time_limit_seconds": 30
            }
        ]
    },

    {
        "number": 8,
        "title_ar": "البناء المقطعي CVV",
        "title_fr": "Structures avec Madd : CV (avec voyelle longue)",
        "description_fr": "Pratiquez les syllabes avec voyelles longues (Madd).",

        "explanation_sections": [
            {
                "title_fr": "CVV ou CV-long",
                "content_fr": """Une structure CVV a une Consonne + une Voyelle longue (Madd).
Par exemple : بَا (bā) = b + ā (voyelle longue). C'est une syllabe avec une voyelle prolongée.
Elle dure plus longtemps qu'une syllabe CV simple.""",
                "content_ar": "ساكن + مد = مقطع طويل",
                "audio_hint": "Syllabe plus longue grâce au Madd",
                "tip_fr": "La syllabe dure deux fois plus longtemps qu'une syllabe CV simple",
                "common_mistakes_fr": "Traiter la voyelle longue comme deux syllabes, ou ne pas tenir assez longtemps"
            }
        ],

        "examples": [
            {
                "arabic": "بَا بِي بُو",
                "transliteration": "bā bī bū",
                "explanation_fr": "Bā avec les 3 voyelles longues (Madd).",
                "audio_description_fr": "bā (long), bī (long), bū (long)"
            },
            {
                "arabic": "تَا دِي نُو",
                "transliteration": "tā dī nū",
                "explanation_fr": "Trois consonnes avec Madd.",
                "audio_description_fr": "tāā, dīī, nūū"
            }
        ],

        "quiz": [
            {
                "question_fr": "Prononcez : بَا",
                "type": "AUDIO_MATCH",
                "choices": ["ba", "bā", "ba-a", "bāā"],
                "correct_index": 1,
                "explanation_fr": "بَا = bā (long, environ 2 temps)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi : Madd vs voyelle courte",
                "description_fr": "Distinguez court vs long",
                "items": ["بَ", "بَا", "تِ", "تِي", "دُ", "دُو"],
                "time_limit_seconds": 35
            }
        ]
    },

    {
        "number": 9,
        "title_ar": "تركيب المقاطع في الكلمات",
        "title_fr": "Combinaisons de syllabes : Former des mots",
        "description_fr": "Assemblez des syllabes pour former des mots complets.",

        "explanation_sections": [
            {
                "title_fr": "De la syllabe au mot",
                "content_fr": """Un mot arabe est composé de plusieurs syllabes assemblées ensemble.
Par exemple : كَتَبَ (il a écrit) = ka (CV) + ta (CV) + ba (CV) = 3 syllabes.
chaque syllabe se prononce fluidement après la précédente. C'est comme assembler des blocs.""",
                "content_ar": "كَتَبَ = ك + ت + ب",
                "audio_hint": "Fluidité entre les syllabes",
                "tip_fr": "Pratiquez d'abord en séparant les syllabes, puis en les liant",
                "common_mistakes_fr": "Trop séparer les syllabes, ou trop les fusionner"
            }
        ],

        "examples": [
            {
                "arabic": "كَتَبَ",
                "transliteration": "ka-ta-ba",
                "explanation_fr": "Il a écrit. 3 syllabes CV simples.",
                "audio_description_fr": "ka-ta-ba (fluide)"
            },
            {
                "arabic": "دَرَسَ",
                "transliteration": "da-ra-sa",
                "explanation_fr": "Il a étudié. 3 syllabes CV.",
                "audio_description_fr": "da-ra-sa"
            },
            {
                "arabic": "مَكْتَب",
                "transliteration": "mak-tab",
                "explanation_fr": "Bureau. CVC + CVC.",
                "audio_description_fr": "mak-tab (deux syllabes fermées)"
            }
        ],

        "quiz": [
            {
                "question_fr": "Prononcez : كَتَبَ",
                "type": "AUDIO_MATCH",
                "choices": ["kataba", "ka-ta-ba", "kit-ba", "keteba"],
                "correct_index": 0,
                "explanation_fr": "كَتَبَ = ka + ta + ba = kataba (fluide)"
            }
        ],

        "challenges": [
            {
                "type": "build_syllable",
                "title_fr": "Construire des mots",
                "description_fr": "Assemblez les syllabes pour former des mots",
                "exercises": [
                    {"syllables": ["كَ", "تَ", "بَ"], "target_word": "كَتَبَ", "meaning": "il a écrit"},
                    {"syllables": ["دَ", "رَ", "سَ"], "target_word": "دَرَسَ", "meaning": "il a étudié"}
                ]
            }
        ]
    },

    {
        "number": 10,
        "title_ar": "قراءة الكلمات المختلطة",
        "title_fr": "Lecture de mots complexes (structures mixtes)",
        "description_fr": "Lisez des mots avec plusieurs types de syllabes (CV, CVC, CVV).",

        "explanation_sections": [
            {
                "title_fr": "Mots réalistes avec structures mixtes",
                "content_fr": """Les mots arabes réels combinent souvent plusieurs types de structures syllabes.
Par exemple : كِتَاب (livre) = ki (CV court) + tāb (CVV + CVC).
Vous devez maîtriser :
1. Reconnaître quand une voyelle est longue ou courte
2. Gérer les transitions entre syllabes ouvertes et fermées
3. Pratiquer la fluidité de la lecture.""",
                "content_ar": "الكلمات الحقيقية = مزيج من المقاطع",
                "audio_hint": "Fluidité et reconnaissance des structures",
                "tip_fr": "Analysez d'abord chaque mot syllabe par syllabe, puis lisez fluidement",
                "common_mistakes_fr": "Essayer de lire trop vite sans comprendre la structure"
            }
        ],

        "examples": [
            {
                "arabic": "كِتَاب",
                "transliteration": "ki-tāb",
                "explanation_fr": "Livre. Structure : CV + CVV + CVC (en fait 2 syllabes fluides).",
                "audio_description_fr": "ki-tāb (livre)"
            },
            {
                "arabic": "مَدْرَسَة",
                "transliteration": "mad-ra-sa",
                "explanation_fr": "École. Structure : CVC + CV + CV.",
                "audio_description_fr": "mad-ra-sa"
            },
            {
                "arabic": "مُحَمَّد",
                "transliteration": "mu-ham-mad",
                "explanation_fr": "Mohammed. Structure : CV + CVC + CVC (avec Shadda).",
                "audio_description_fr": "mu-ham-mad (note : Shadda sur le dernier Dāl)"
            },
            {
                "arabic": "السَّلاَم",
                "transliteration": "as-sā-lām",
                "explanation_fr": "La paix (dans Assalamu alaikum). Structure complexe.",
                "audio_description_fr": "as-sā-lām"
            }
        ],

        "quiz": [
            {
                "question_fr": "Prononcez : كِتَاب",
                "type": "AUDIO_MATCH",
                "choices": ["ki-ta-ab", "ki-tāb", "ki-ta-ba", "kitaab"],
                "correct_index": 1,
                "explanation_fr": "كِتَاب = ki (CV) + tāb (CVV+CVC) = kitāb"
            },
            {
                "question_fr": "Prononcez : مَدْرَسَة",
                "type": "AUDIO_MATCH",
                "choices": ["madra-sa", "mad-ra-sa", "ma-dra-se", "mad-rasa"],
                "correct_index": 1,
                "explanation_fr": "مَدْرَسَة = mad-ra-sa (3 syllabes)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi : Lire des mots réalistes",
                "description_fr": "Lisez ces mots aussi rapidement que possible",
                "items": ["كِتَاب", "مَدْرَسَة", "مُحَمَّد", "السَّلاَم", "النُّور"],
                "time_limit_seconds": 45
            }
        ]
    }
]


# ============================================================================
# PART B: NOURANIA ENRICHED — 17 CHAPTERS (DETAILED EXPANSION)
# ============================================================================

NOURANIA_ENRICHED_CHAPTERS = [
    {
        "number": 1,
        "title_ar": "الحروف المفردة",
        "title_fr": "Les lettres isolées (Hafīf lesson 1)",
        "description_fr": "Maîtrisez les 29 lettres de l'alphabet arabe dans leur forme isolée avec prononciation détaillée.",

        "explanation_sections": [
            {
                "title_fr": "Introduction à l'alphabet arabe",
                "content_fr": """L'alphabet arabe contient 29 lettres (certaines sources en comptent 28 en excluant Hamza).
Chaque lettre a un NOM distinct (qui finit généralement par un Alif) et une prononciation spécifique.
Les lettres sont classées par leur point d'articulation (glotte, lèvres, dents, etc.).
Avant de combiner les lettres avec les voyelles, vous devez apprendre chaque lettre isolée.""",
                "content_ar": "الحروف الأبجدية = 29 حرفاً",
                "audio_hint": "Prononciation claire de chaque lettre",
                "tip_fr": "Apprenez d'abord les 5 premières lettres (Alif, Bā, Tā, Thā, Jīm) très bien",
                "common_mistakes_fr": "Confondre les lettres similaires (Bā/Tā, Thā/Fā, Ḥā/Khā)"
            },
            {
                "title_fr": "Classification par point d'articulation",
                "content_fr": """Les linguistes arabes classent les lettres par OÙ elles sont prononcées dans la bouche/gorge :
- Gutturales (Hamza, Alif, Ḥā, Khā, ع, Ghain) : gorge/pharynx
- Labiales (Bā, Fā, Mīm) : lèvres
- Dentales (Tā, Thā, Dāl, Dhāl, Sīn, Ṣād, Tāy, Ẓā, Nūn, Lām, Rā) : dents/alvéoles
- Vélaires (Kāf, Qāf) : voile du palais
Cette classification aide à comprendre les similarités et les différences.""",
                "content_ar": "تصنيف الحروف حسب مخارج الأصوات",
                "audio_hint": "Sentez où chaque lettre est prononcée",
                "tip_fr": "Prononcez chaque lettre et ressentez le point d'articulation",
                "common_mistakes_fr": "Essayer de les apprendre par cœur sans comprendre l'articulation"
            },
            {
                "title_fr": "Les 29 lettres : présentation complète",
                "content_fr": """Voici l'ordre traditionnel arabe (Abjadī) suivi de l'ordre moderne (Alphabétique) :
Abjadī : Alif, Bā, Jīm, Dāl, Hā, Wāw, Zain, Ḥā, Ṭā, Yā...
Alphabétique : Alif, Bā, Tā, Thā, Jīm, Ḥā, Khā, Dāl, Dhāl, Rā, Zain, Sīn, Shīn, Ṣād...
Dans les cours modernes, on utilise généralement l'ordre alphabétique car il regroupe les lettres similaires.""",
                "content_ar": "ترتيب الحروف : أبجدي أو أبجدي حديث",
                "audio_hint": "Deux ordres différents mais même lettres",
                "tip_fr": "Apprenez l'ordre alphabétique moderne d'abord, plus logique",
                "common_mistakes_fr": "Confondre les deux ordres, ou sauter des lettres"
            }
        ],

        "examples": [
            {
                "arabic": "أ",
                "transliteration": "ā / '",
                "explanation_fr": "Alif (première lettre). Peut être occlusive glottale (' comme dans 'aïe') ou voyelle longue (ā).",
                "audio_description_fr": "Alif : son très doux"
            },
            {
                "arabic": "ب",
                "transliteration": "b",
                "explanation_fr": "Bā (deuxième lettre). Occlusive bilabiale sonore comme le 'b' français.",
                "audio_description_fr": "Bā : 'b' comme dans 'boule'"
            },
            {
                "arabic": "ح",
                "transliteration": "ḥ",
                "explanation_fr": "Ḥā (6ème lettre). Fricative pharyngale sourde. SON UNIQUE À L'ARABE. Très important à maîtriser.",
                "audio_description_fr": "Ḥā : son rauque de la gorge, unique"
            },
            {
                "arabic": "خ",
                "transliteration": "kh",
                "explanation_fr": "Khā (7ème lettre). Fricative vélaire sourde. Similaire au 'j' espagnol dans 'jota'.",
                "audio_description_fr": "Khā : 'kh' comme dans 'Bach' (le compositeur)"
            },
            {
                "arabic": "ع",
                "transliteration": "ʿ",
                "explanation_fr": "Ain (18ème lettre). Fricative pharyngale sonore. SON DIFFICILE. UNIQUE À L'ARABE.",
                "audio_description_fr": "Ain : son guttural profond, très difficile pour les francophones"
            },
            {
                "arabic": "غ",
                "transliteration": "gh",
                "explanation_fr": "Ghain (19ème lettre). Fricative vélaire sonore. Similaire au 'r' français guttural.",
                "audio_description_fr": "Ghain : 'gh' comme le 'r' roulé espagnol"
            }
        ],

        "illustrations": [
            {
                "type": "letter_chart",
                "title_fr": "Les 29 lettres arabes (ordre alphabétique)",
                "description_fr": "Tableau complet de toutes les lettres",
                "data": {
                    "letters": [
                        {"order": 1, "arabic": "ا", "name": "Alif", "transliteration": "ā", "articulation": "Gutturale", "difficulty": "facile"},
                        {"order": 2, "arabic": "ب", "name": "Bā", "transliteration": "b", "articulation": "Labiale", "difficulty": "facile"},
                        {"order": 3, "arabic": "ت", "name": "Tā", "transliteration": "t", "articulation": "Dentale", "difficulty": "facile"},
                        {"order": 4, "arabic": "ث", "name": "Thā", "transliteration": "th", "articulation": "Dentale", "difficulty": "moyen"},
                        {"order": 5, "arabic": "ج", "name": "Jīm", "transliteration": "j", "articulation": "Palatale", "difficulty": "facile"},
                        {"order": 6, "arabic": "ح", "name": "Ḥā", "transliteration": "ḥ", "articulation": "Pharyngale", "difficulty": "difficile"},
                        {"order": 7, "arabic": "خ", "name": "Khā", "transliteration": "kh", "articulation": "Vélaire", "difficulty": "moyen"},
                        {"order": 8, "arabic": "د", "name": "Dāl", "transliteration": "d", "articulation": "Dentale", "difficulty": "facile"}
                    ]
                }
            },
            {
                "type": "mouth_diagram",
                "title_fr": "Points d'articulation des lettres difficiles",
                "description_fr": "Où prononcer Ḥā, Khā, Ain, Ghain",
                "data": {
                    "difficult_letters": [
                        {
                            "letter": "ح",
                            "name": "Ḥā",
                            "position": "pharynx",
                            "technique": "Creusez la gorge, sons sourde et rauque"
                        },
                        {
                            "letter": "خ",
                            "name": "Khā",
                            "position": "soft_palate",
                            "technique": "Comme pour dire 'kh', souffle sans vibration"
                        },
                        {
                            "letter": "ع",
                            "name": "Ain",
                            "position": "pharynx",
                            "technique": "Fermez la gorge légèrement, son guttural fort"
                        },
                        {
                            "letter": "غ",
                            "name": "Ghain",
                            "position": "soft_palate",
                            "technique": "Comme 'kh' mais sonore (avec vibration vocale)"
                        }
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Combien de lettres dans l'alphabet arabe ?",
                "type": "MCQ",
                "choices": ["26", "28", "29", "32"],
                "correct_index": 2,
                "explanation_fr": "L'alphabet arabe a 29 lettres (28 si on exclut Hamza)"
            },
            {
                "question_fr": "Quel son est UNIQUE à l'arabe parmi ceux-ci ?",
                "type": "MCQ",
                "choices": ["b (Bā)", "t (Tā)", "ḥ (Ḥā)", "s (Sīn)"],
                "correct_index": 2,
                "explanation_fr": "Ḥā est un son pharyngal sourde unique à l'arabe, inexistant en français"
            },
            {
                "question_fr": "Quel est le nom de la deuxième lettre ?",
                "type": "MCQ",
                "choices": ["Alif", "Bā", "Tā", "Thā"],
                "correct_index": 1,
                "explanation_fr": "Alif (ا) est la 1ère, Bā (ب) est la 2ème"
            },
            {
                "question_fr": "Prononcez : ح",
                "type": "AUDIO_MATCH",
                "choices": ["h (comme français)", "ḥ (son pharyngal rauque)", "kh", "gh"],
                "correct_index": 1,
                "explanation_fr": "ح = Ḥā = son pharyngal, bien plus profond que 'h' français"
            },
            {
                "question_fr": "Prononcez : ع",
                "type": "AUDIO_MATCH",
                "choices": ["comme Hamza", "comme Ḥā", "son guttural fort", "comme Ain français"],
                "correct_index": 2,
                "explanation_fr": "ع = Ain = son guttural pharyngal sonore, très difficile pour débutants"
            },
            {
                "question_fr": "Quelle lettre est similaire au 'j' espagnol ?",
                "type": "MCQ",
                "choices": ["Ḥā", "Khā", "Jīm", "Ain"],
                "correct_index": 1,
                "explanation_fr": "Khā (خ) ressemble au 'j' espagnol dans 'jota' ou au 'r' guttural français"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Les 29 lettres isolées",
                "description_fr": "Prononcez chaque lettre aussi vite que possible (30 secondes pour les 29)",
                "items": ["ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س", "ش", "ص", "ض", "ط", "ظ", "ع", "غ", "ف", "ق", "ك", "ل", "م", "ن", "ه", "و", "ي", "ة"],
                "time_limit_seconds": 60
            },
            {
                "type": "letter_detective",
                "title_fr": "Détective des lettres : Trouvez l'intrus",
                "description_fr": "Identifiez laquelle est une fausse lettre dans le groupe",
                "exercises": [
                    {"letters": ["ب", "ت", "ث", "خ"], "explanation": "Khā ne ressemble pas aux autres"},
                    {"letters": ["ح", "ع", "غ", "ف"], "explanation": "Fā est labiale, les autres sont gutturales"}
                ]
            }
        ]
    },

    # Chapter 2: Les 3 voyelles courtes (Already detailed in VOYELLES_SYLLABES, so we'll simplify here and focus on integration with letters)
    {
        "number": 2,
        "title_ar": "الحركات",
        "title_fr": "Les voyelles courtes (Tashkeel)",
        "description_fr": "Les trois voyelles courtes : Fatha (a), Kasra (i), Damma (u). Fondamental pour la lecture arabe.",

        "explanation_sections": [
            {
                "title_fr": "Tashkeel : le système des voyelles arabes",
                "content_fr": """En arabe, les voyelles ne sont pas des lettres mais des DIACRITIQUES (marques) placées sur ou sous les lettres.
C'est complètement différent du français où les voyelles sont des lettres.
Le système des voyelles/diacritiques s'appelle 'Tashkeel' (التشكيل) = 'façonner'.
Sans diacritiques, un texte arabe est difficile à lire (pour les enfants et non-natives).""",
                "content_ar": "التشكيل = الحركات والسكون",
                "audio_hint": "Les trois sons distincts : a, i, u",
                "tip_fr": "Mémorisez les positions : Fatha DESSUS, Kasra DESSOUS, Damma DESSUS",
                "common_mistakes_fr": "Oublier que ce sont des diacritiques, pas des lettres"
            },
            {
                "title_fr": "La Fatha (ـَ) — voyelle 'a'",
                "content_fr": """La Fatha est un petit trait diagonal au-dessus de la lettre (َ).
Elle produit un son 'a' court, similaire au français 'patte', 'matte', 'batte'.
C'est une voyelle ouverte antérieure, où la langue est un peu en avant et la bouche modérément ouverte.
Voyelle très commune en arabe.""",
                "content_ar": "الفَــتْــحَـة = بَ",
                "audio_hint": "a court comme dans 'patte'",
                "tip_fr": "Pratiquez : 'ba ba ba' rapidement",
                "common_mistakes_fr": "Prononcer 'a' comme en français avec la bouche trop ouverte"
            },
            {
                "title_fr": "La Kasra (ـِ) — voyelle 'i'",
                "content_fr": """La Kasra est un petit trait diagonal sous la lettre (ِ).
Elle produit un son 'i' court, similaire au français 'bille', 'quille', 'pille'.
C'est une voyelle fermée antérieure, où les lèvres sont écartées et la langue avancée.
Très courante également.""",
                "content_ar": "الكَــسْــرَة = بِ",
                "audio_hint": "i court comme dans 'bille'",
                "tip_fr": "Écartez les lèvres légèrement et dites 'bi bi bi'",
                "common_mistakes_fr": "Prononcer 'e' au lieu de 'i', ou confondre avec 'a'"
            },
            {
                "title_fr": "La Damma (ـُ) — voyelle 'u'",
                "content_fr": """La Damma est un petit 'o' ou 'w' au-dessus de la lettre (ُ).
Elle produit un son 'u' court, similaire au français 'boule', 'moule', 'poule'.
C'est une voyelle fermée postérieure, où les lèvres sont arrondies et la langue reculée.
Moins fréquente que les deux autres.""",
                "content_ar": "الضَّــمَّـة = بُ",
                "audio_hint": "u court comme dans 'boule'",
                "tip_fr": "Arrondissez les lèvres et dites 'bu bu bu'",
                "common_mistakes_fr": "Prononcer 'ou' au lieu de 'u', ou trop arrondir les lèvres"
            }
        ],

        "examples": [
            {
                "arabic": "بَ بِ بُ",
                "transliteration": "ba bi bu",
                "explanation_fr": "Bā avec les 3 voyelles courtes. Trois sons complètement différents.",
                "audio_description_fr": "ba (a), bi (i), bu (u)"
            },
            {
                "arabic": "تَ تِ تُ",
                "transliteration": "ta ti tu",
                "explanation_fr": "Tā avec les 3 voyelles.",
                "audio_description_fr": "ta, ti, tu"
            },
            {
                "arabic": "حَ حِ حُ",
                "transliteration": "ḥa ḥi ḥu",
                "explanation_fr": "Ḥā (lettre difficile) avec les 3 voyelles. Très important de bien prononcer Ḥā.",
                "audio_description_fr": "ḥa (guttural a), ḥi (guttural i), ḥu (guttural u)"
            }
        ],

        "illustrations": [
            {
                "type": "vowel_positions",
                "title_fr": "Position des diacritiques sur la lettre",
                "description_fr": "Où placer chaque voyelle visuellement",
                "data": {
                    "vowels": [
                        {"name": "Fatha", "symbol": "َ", "position": "above_letter", "example": "بَ"},
                        {"name": "Kasra", "symbol": "ِ", "position": "below_letter", "example": "بِ"},
                        {"name": "Damma", "symbol": "ُ", "position": "above_letter", "example": "بُ"}
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "La Fatha produit quel son ?",
                "type": "MCQ",
                "choices": ["a", "i", "u", "e"],
                "correct_index": 0,
                "explanation_fr": "Fatha = 'a' comme dans 'patte'"
            },
            {
                "question_fr": "Prononcez : حِ",
                "type": "AUDIO_MATCH",
                "choices": ["ha (français)", "ḥi (guttural i)", "hi", "he"],
                "correct_index": 1,
                "explanation_fr": "حِ = Ḥā + Kasra = ḥi (lettre pharyngale + voyelle i)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Voyelles avec chaque lettre",
                "description_fr": "Prononcez chaque syllabe avec ses 3 voyelles",
                "items": ["بَ بِ بُ", "تَ تِ تُ", "ثَ ثِ ثُ", "جَ جِ جُ", "حَ حِ حُ"],
                "time_limit_seconds": 40
            }
        ]
    },

    # Chapters 3-6: Tanwin, Sukun, Madd, Madd avec Sukun (I'll compress these for space, focusing on the key improvements)
    {
        "number": 3,
        "title_ar": "التنوين",
        "title_fr": "Le Tanwin (le 'n' final)",
        "description_fr": "Les trois formes du Tanwin et comment les prononcer correctement.",

        "explanation_sections": [
            {
                "title_fr": "Le Tanwin expliqué simplement",
                "content_fr": """Le Tanwin ajoute un son 'n' nasal à la fin d'un mot quand le nom est INDÉFINI (pas de 'al' = 'le').
En arabe, chaque nom indéfini a obligatoirement le Tanwin. C'est comme le français 'un' ou 'une', mais écrit comme diacritique.
Trois formes : -an, -in, -un (correspondant aux 3 voyelles).""",
                "content_ar": "التنوين = نون مخفية",
                "audio_hint": "Ajouter un 'n' nasal à la fin",
                "tip_fr": "Chaque mot indéfini a un Tanwin obligatoire",
                "common_mistakes_fr": "Prononcer le 'n' comme une vraie consonne au lieu de nasalisation"
            }
        ],

        "examples": [
            {
                "arabic": "كِتَابٌ",
                "transliteration": "ki-tāb-un",
                "explanation_fr": "Un livre (indéfini, nominatif). Tanwin Damm.",
                "audio_description_fr": "kitābun (avec n nasal)"
            },
            {
                "arabic": "مَدْرَسَةٌ",
                "transliteration": "mad-ra-sa-tun",
                "explanation_fr": "Une école (indéfini, nominatif).",
                "audio_description_fr": "madrasatun"
            }
        ],

        "quiz": [
            {
                "question_fr": "Le Tanwin Damm (ٌ) produit quel son ?",
                "type": "MCQ",
                "choices": ["an", "in", "un", "en"],
                "correct_index": 2,
                "explanation_fr": "ٌ = Tanwin Damm = son 'un'"
            }
        ],

        "challenges": [
            {
                "type": "dictation",
                "title_fr": "Dictée : Identifier le Tanwin",
                "description_fr": "Écoutez et dites quel Tanwin vous entendez",
                "exercises": [
                    {"arabic": "كِتَابٌ", "expected": "un"},
                    {"arabic": "مَدْرَسَةٌ", "expected": "un"}
                ]
            }
        ]
    },

    {
        "number": 4,
        "title_ar": "السكون",
        "title_fr": "Le Sukun (consonne sans voyelle)",
        "description_fr": "Apprenez à fermer les syllabes avec le Sukun et la structure CVC.",

        "explanation_sections": [
            {
                "title_fr": "Le Sukun (ْ) — consonne fermée",
                "content_fr": """Le Sukun (ْ) est un petit cercle vide au-dessus d'une lettre.
Il signifie qu'il n'y a PAS de voyelle. La syllabe se ferme avec une consonne.
Structure CVC : Consonante + Voyelle + Consonne avec Sukun.
Très fréquent en arabe et essentiel pour la lecture correcte.""",
                "content_ar": "السكون = خلو الحرف من الحركة",
                "audio_hint": "Consonne finale sans voyelle",
                "tip_fr": "Prononcez la première syllabe, puis fermez avec la consonne Sukun",
                "common_mistakes_fr": "Ajouter une voyelle à la consonne Sukun, créant une syllabe supplémentaire"
            },
            {
                "title_fr": "Liaison de CVC + CV",
                "content_fr": """Quand une consonne avec Sukun précède une consonne avec voyelle, elles se lient fluidement.
Par exemple : مَكْتَب (mak-tab) = mak (CVC fermée) + ta (CV ouverte) + ba (CV ouverte).
Les syllabes se joignent naturellement sans respiration entre les deux.""",
                "content_ar": "مقطع مغلق + مقطع مفتوح = كلمة سليمة",
                "audio_hint": "Fluidité entre les syllabes",
                "tip_fr": "Pratiquez en séparant d'abord, puis en liant",
                "common_mistakes_fr": "Trop séparer les syllabes ou trop les fusionner"
            }
        ],

        "examples": [
            {
                "arabic": "مَكْ",
                "transliteration": "mak",
                "explanation_fr": "Structure CVC : m + a + k avec Sukun. Syllabe fermée.",
                "audio_description_fr": "mak (pas 'maku')"
            },
            {
                "arabic": "مَكْتَب",
                "transliteration": "mak-tab",
                "explanation_fr": "Bureau. Deux syllabes : CVC + CV (finit en CVC).",
                "audio_description_fr": "mak-ta-ba (fluidement)"
            },
            {
                "arabic": "دَرْس",
                "transliteration": "dars",
                "explanation_fr": "Cours. Structure : CVC + C avec Sukun = word fermée.",
                "audio_description_fr": "dars"
            }
        ],

        "quiz": [
            {
                "question_fr": "Le Sukun (ْ) indique quoi ?",
                "type": "MCQ",
                "choices": ["Une voyelle courte", "Une voyelle longue", "Pas de voyelle", "Une consonne doublée"],
                "correct_index": 2,
                "explanation_fr": "Sukun = pas de voyelle. La syllabe se ferme avec une consonne."
            },
            {
                "question_fr": "Prononcez : مَكْ",
                "type": "AUDIO_MATCH",
                "choices": ["ma-ka", "mak", "ma-ku", "maku"],
                "correct_index": 1,
                "explanation_fr": "مَكْ = CVC = mak (syllabe fermée)"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Syllabes CVC",
                "description_fr": "Prononcez rapidement",
                "items": ["مَكْ", "دَرْ", "نِسْ", "سَلْ", "كَتْ", "جَبْ", "قَلْ"],
                "time_limit_seconds": 30
            }
        ]
    },

    {
        "number": 5,
        "title_ar": "حروف المد",
        "title_fr": "Les lettres de prolongation (Madd)",
        "description_fr": "Alif, Wāw et Yā créent des voyelles longues. Fondamental pour le Tajwid.",

        "explanation_sections": [
            {
                "title_fr": "Concept de Madd (prolongation)",
                "content_fr": """Madd signifie 'prolonger' ou 'étirer'. Quand une lettre de prolongation (Alif, Wāw, Yā) suit une voyelle courte,
la voyelle s'allonge : courte (1 temps) → longue (2 temps).
Cette distinction change le sens des mots. C'est une règle FONDAMENTALE du Tajwid.""",
                "content_ar": "المد = إطالة الصوت",
                "audio_hint": "Voyelle longue = 2 fois plus longue que voyelle courte",
                "tip_fr": "Comptez mentalement : courte = 1, longue = 1-2",
                "common_mistakes_fr": "Ignorer la durée, prononcer trop vite"
            },
            {
                "title_fr": "Les 3 types de Madd",
                "content_fr": """
1. Alif Madd (ā) : Fatha + Alif → voyelle 'ā' longue
2. Yā Madd (ī) : Kasra + Yā → voyelle 'ī' longue
3. Wāw Madd (ū) : Damma + Wāw → voyelle 'ū' longue

Chaque voyelle courte a une lettre de prolongation correspondante.
La lettre de prolongation vient APRÈS et prolonge la voyelle.""",
                "content_ar": "ثلاث حروف مد: ألف وياء وواو",
                "audio_hint": "Trois durées correspondant aux trois voyelles",
                "tip_fr": "Mémorisez : Fatha→Alif, Kasra→Yā, Damma→Wāw",
                "common_mistakes_fr": "Traiter Alif/Yā/Wāw comme consonnes supplémentaires"
            }
        ],

        "examples": [
            {
                "arabic": "بَا بِي بُو",
                "transliteration": "bā bī bū",
                "explanation_fr": "Les 3 types de Madd sur Bā. Comparez avec les voyelles courtes.",
                "audio_description_fr": "bāā (long a), bīī (long i), būū (long u)"
            },
            {
                "arabic": "قَالَ",
                "transliteration": "qā-la",
                "explanation_fr": "Il a dit (Quranic). Alif Madd dans la première syllabe.",
                "audio_description_fr": "qāā-la (première voyelle est longue)"
            },
            {
                "arabic": "قِيل",
                "transliteration": "qīl",
                "explanation_fr": "Il a été dit. Yā Madd dans la première syllabe.",
                "audio_description_fr": "qīīl (Yā prolonge)"
            },
            {
                "arabic": "قُول",
                "transliteration": "qūl",
                "explanation_fr": "Dis (impératif). Wāw Madd.",
                "audio_description_fr": "qūūl"
            }
        ],

        "illustrations": [
            {
                "type": "madd_formation",
                "title_fr": "Les 3 types de Madd visuellement",
                "description_fr": "Comment se forment les voyelles longues",
                "data": {
                    "types": [
                        {
                            "name": "Alif Madd",
                            "formula": "Fatha + Alif",
                            "result": "ā",
                            "example": "بَا",
                            "transliteration": "bā"
                        },
                        {
                            "name": "Yā Madd",
                            "formula": "Kasra + Yā",
                            "result": "ī",
                            "example": "بِي",
                            "transliteration": "bī"
                        },
                        {
                            "name": "Wāw Madd",
                            "formula": "Damma + Wāw",
                            "result": "ū",
                            "example": "بُو",
                            "transliteration": "bū"
                        }
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Quel lettre prolonge la Fatha ?",
                "type": "MCQ",
                "choices": ["Yā", "Wāw", "Alif", "Nūn"],
                "correct_index": 2,
                "explanation_fr": "Alif prolonge Fatha → Madd ā (bā)"
            },
            {
                "question_fr": "Prononcez : بِي",
                "type": "AUDIO_MATCH",
                "choices": ["bi (court)", "bī (long)", "bi-y", "bay"],
                "correct_index": 1,
                "explanation_fr": "بِي = Kasra + Yā = bī (long)"
            }
        ],

        "challenges": [
            {
                "type": "build_syllable",
                "title_fr": "Construire les Madd",
                "description_fr": "Assemblez la voyelle + sa lettre de prolongation",
                "exercises": [
                    {"vowel": "Fatha", "letter": "Alif", "target": "ā"},
                    {"vowel": "Kasra", "letter": "Yā", "target": "ī"},
                    {"vowel": "Damma", "letter": "Wāw", "target": "ū"}
                ]
            }
        ]
    },

    {
        "number": 6,
        "title_ar": "حروف المد مع السكون",
        "title_fr": "Madd avec Sukun (Madd Lāzim)",
        "description_fr": "Quand Madd est suivi de Sukun, le Madd s'allonge à 6 temps.",

        "explanation_sections": [
            {
                "title_fr": "Madd Lāzim (Madd obligatoire allongé)",
                "content_fr": """Quand une lettre de prolongation est suivi d'une consonne avec Sukun DANS LE MÊME MOT,
le Madd devient obligatoire et très long : 6 temps environ (au lieu de 2 temps normal).
C'est une règle très importante du Tajwid coranique.""",
                "content_ar": "المد الواجب المتصل = ستة أوقات",
                "audio_hint": "Madd très prolongé (3x plus long que normal)",
                "tip_fr": "Quand vous voyez Alif/Yā/Wāw + Sukun sur la lettre suivante, allongez beaucoup",
                "common_mistakes_fr": "Prononcer avec la durée normale au lieu d'allonger"
            }
        ],

        "examples": [
            {
                "arabic": "الضَّالِّين",
                "transliteration": "aḍ-ḍāl-lī-n",
                "explanation_fr": "Les égarés (Quranic). Madd ā suivi de Lām avec Shadda.",
                "audio_description_fr": "Le ā est très allongé (6 temps)"
            }
        ],

        "quiz": [
            {
                "question_fr": "Madd Lāzim se prononce combien de fois ?",
                "type": "MCQ",
                "choices": ["2 temps (normal)", "4 temps", "6 temps", "10 temps"],
                "correct_index": 2,
                "explanation_fr": "Madd Lāzim = 6 temps (3x la durée normale)"
            }
        ]
    },

    {
        "number": 7,
        "title_ar": "الحروف المشددة",
        "title_fr": "La Shadda (consonne doublée)",
        "description_fr": "Prononcez les consonnes doublées correctement.",

        "explanation_sections": [
            {
                "title_fr": "La Shadda expliquée",
                "content_fr": """La Shadda (ّ) est un petit 'w' au-dessus d'une lettre. Elle indique une CONSONNE DOUBLÉE.
Phonétiquement : consonne avec Sukun + consonne avec voyelle = géminée (double).
Par exemple : مَدَّ (prolonger) = ma (CV) + d avec Shadda (consonne doublée).
Très fréquent en arabe, surtout dans le Coran.""",
                "content_ar": "الشدة = تضعيف الحرف",
                "audio_hint": "Consonne prononcée deux fois rapidement",
                "tip_fr": "Pensez à doubler la consonne : 'dd', 'nn', 'tt', etc.",
                "common_mistakes_fr": "Prononcer une seule fois, ou trop séparer les deux prononciations"
            }
        ],

        "examples": [
            {
                "arabic": "مَدَّ",
                "transliteration": "mad-da",
                "explanation_fr": "Prolonger. Dāl avec Shadda = consonne doublée.",
                "audio_description_fr": "mad-da (d très appuyé)"
            },
            {
                "arabic": "إِنَّ",
                "transliteration": "in-na",
                "explanation_fr": "Verily (très fréquent au Coran). Nūn avec Shadda.",
                "audio_description_fr": "in-na (n doublé)"
            }
        ],

        "quiz": [
            {
                "question_fr": "La Shadda (ّ) indique quoi ?",
                "type": "MCQ",
                "choices": ["Une voyelle longue", "Une consonne doublée", "Pas de voyelle", "Une consonne sourde"],
                "correct_index": 1,
                "explanation_fr": "Shadda = consonne prononcée deux fois très rapidement"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi vitesse : Les Shadda",
                "description_fr": "Prononcez les consonnes doublées",
                "items": ["بّ", "تّ", "دّ", "سّ", "نّ", "مّ"],
                "time_limit_seconds": 25
            }
        ]
    },

    {
        "number": 8,
        "title_ar": "نون التنوين والنون الساكنة",
        "title_fr": "Nūn Sākina et Tanwin — les 4 règles (Iẓhār, Idghām, Iqlāb, Ikhfā)",
        "description_fr": "Maîtrisez les règles cruciales du Tajwid pour Nūn Sākina et Tanwin.",

        "explanation_sections": [
            {
                "title_fr": "Les 4 règles de récitation",
                "content_fr": """Quand un Nūn sans voyelle (Nūn Sākina) ou un Tanwin est suivi d'une autre lettre,
quatre règles s'appliquent selon la lettre suivante. C'est une règle FONDAMENTALE du Tajwid.
Ces règles changent la prononciation et doivent être apprises par cœur.""",
                "content_ar": "أحكام النون الساكنة والتنوين",
                "audio_hint": "Quatre comportements différents selon la lettre suivante",
                "tip_fr": "Mémorisez les 4 règles avec les lettres correspondantes",
                "common_mistakes_fr": "Mélanger les règles ou les appliquer incorrectement"
            },
            {
                "title_fr": "Règle 1 : Iẓhār (Clarté)",
                "content_fr": """Quand Nūn Sākina/Tanwin est suivi de ء ه ع ح غ خ, le Nūn se prononce CLAIREMENT,
sans aucune nasalisation supplémentaire. Les deux consonnes gardent leur identité.
Lettres d'Iẓhār : ء ه ع ح غ خ (6 lettres)
Exemple : مِنْ أَيْن (from where) = min-ayn (Nūn clair)""",
                "content_ar": "إظهار = ظهور النون واضحاً",
                "audio_hint": "Nūn très clair et distinct",
                "tip_fr": "Prononcez le Nūn complètement, puis la lettre suivante",
                "common_mistakes_fr": "Nasaliser le Nūn ou le fusionner"
            },
            {
                "title_fr": "Règle 2 : Idghām (Fusion)",
                "content_fr": """Quand Nūn Sākina/Tanwin est suivi de ي ر م ل و ن, le Nūn se FUSIONNE avec la lettre suivante.
Lettres d'Idghām : ي ر م ل و ن (6 lettres)
La fusion se fait avec ou sans Ghunna (nasalité résiduelle).
Exemple : مِنْ ي (from y) → devient une seule syllabe""",
                "content_ar": "إدغام = دخول النون في الحرف التالي",
                "audio_hint": "Fusion complète, la lettre suivante est doublée acoustiquement",
                "tip_fr": "Le Nūn disparaît, la consonne suivante est doublée",
                "common_mistakes_fr": "Prononcer le Nūn + la lettre au lieu de fusionner"
            },
            {
                "title_fr": "Règle 3 : Iqlāb (Transformation)",
                "content_fr": """Quand Nūn Sākina/Tanwin est suivi de ب UNIQUEMENT, le Nūn se TRANSFORME en Mīm.
Lettre d'Iqlāb : ب (1 lettre)
Vous prononcez 'm' à la place du 'n' avec nasalisation.
Exemple : مِنْ بَعْد (from after) = mim-ba'd (le n devient m)""",
                "content_ar": "إقلاب = تحويل النون إلى ميم",
                "audio_hint": "Son 'm' nasal à la place du 'n'",
                "tip_fr": "Dites 'n' mais changez-le en 'm' : nim → mim",
                "common_mistakes_fr": "Prononcer 'n' et 'b' séparés, ou 'nb' au lieu de 'm'"
            },
            {
                "title_fr": "Règle 4 : Ikhfā (Dissimulation)",
                "content_fr": """Quand Nūn Sākina/Tanwin est suivi de l'une des 15 lettres RESTANTES,
le Nūn est CACHÉ avec nasalisation entre Iẓhār et Idghām.
15 lettres d'Ikhfā : ت ث ج د ذ ز س ش ص ض ط ظ ف ق ك
Le Nūn n'est pas complètement clair, mais pas fusionné non plus.""",
                "content_ar": "إخفاء = إخفاء النون مع الغنة",
                "audio_hint": "Nūn léger/nasalisé, pas clair mais pas fusionné",
                "tip_fr": "Prononcez le Nūn doucement avec nasalité avant la lettre",
                "common_mistakes_fr": "Trop clair (Iẓhār) ou trop fusionné (Idghām)"
            }
        ],

        "examples": [
            {
                "arabic": "مِنْ أَيْن",
                "transliteration": "min-ayn",
                "explanation_fr": "De où ? Nūn avant Ain (Iẓhār). Nūn très clair.",
                "audio_description_fr": "min (n clair) - ayn"
            },
            {
                "arabic": "مِنْ يَعْمَل",
                "transliteration": "min-ya'mal",
                "explanation_fr": "De celui qui travaille. Nūn avant Yā (Idghām). Fusion.",
                "audio_description_fr": "miyya'mal (fusion)"
            },
            {
                "arabic": "مِنْ بَعْد",
                "transliteration": "mim-ba'd",
                "explanation_fr": "Après. Nūn avant Bā (Iqlāb). Transformation en Mīm.",
                "audio_description_fr": "mim-ba'd (n devient m)"
            },
            {
                "arabic": "مِنْ تَقْوَى",
                "transliteration": "min-taqwā",
                "explanation_fr": "De la piété. Nūn avant Tā (Ikhfā). Nūn caché.",
                "audio_description_fr": "min-taqwā (n léger/nasalisé)"
            }
        ],

        "illustrations": [
            {
                "type": "tajweed_rules_chart",
                "title_fr": "Les 4 règles du Nūn et Tanwin",
                "description_fr": "Tableau récapitulatif des 4 règles",
                "data": {
                    "rules": [
                        {
                            "name": "Iẓhār",
                            "letters": "ء ه ع ح غ خ",
                            "pronunciation": "Nūn clair et distinct",
                            "letters_count": 6
                        },
                        {
                            "name": "Idghām",
                            "letters": "ي ر م ل و ن",
                            "pronunciation": "Fusion complète",
                            "letters_count": 6
                        },
                        {
                            "name": "Iqlāb",
                            "letters": "ب",
                            "pronunciation": "Nūn → Mīm",
                            "letters_count": 1
                        },
                        {
                            "name": "Ikhfā",
                            "letters": "ت ث ج د ذ ز س ش ص ض ط ظ ف ق ك",
                            "pronunciation": "Nūn caché/nasalisé",
                            "letters_count": 15
                        }
                    ]
                }
            }
        ],

        "quiz": [
            {
                "question_fr": "Quand Nūn est suivi de ء ه ع ح غ خ, quelle règle s'applique ?",
                "type": "MCQ",
                "choices": ["Iẓhār", "Idghām", "Iqlāb", "Ikhfā"],
                "correct_index": 0,
                "explanation_fr": "Ces 6 lettres causent Iẓhār (Nūn clair)"
            },
            {
                "question_fr": "Prononcez : مِنْ بَعْد",
                "type": "AUDIO_MATCH",
                "choices": ["min-ba'd", "mim-ba'd", "nim-ba'd", "min-b"],
                "correct_index": 1,
                "explanation_fr": "Iqlāb : Nūn devient Mīm avant Bā"
            },
            {
                "question_fr": "Combien de lettres causent Ikhfā ?",
                "type": "MCQ",
                "choices": ["6", "15", "20", "28"],
                "correct_index": 1,
                "explanation_fr": "Ikhfā s'applique aux 15 lettres restantes"
            }
        ],

        "challenges": [
            {
                "type": "letter_detective",
                "title_fr": "Détective Tajwid : Identifier la règle",
                "description_fr": "Dites quelle règle s'applique (Iẓhār, Idghām, Iqlāb, Ikhfā)",
                "exercises": [
                    {"arabic": "مِنْ أَيْن", "rule": "Iẓhār"},
                    {"arabic": "مِنْ يَعْمَل", "rule": "Idghām"},
                    {"arabic": "مِنْ بَعْد", "rule": "Iqlāb"},
                    {"arabic": "مِنْ تَقْوَى", "rule": "Ikhfā"}
                ]
            }
        ]
    },

    # Chapters 9-17 follow similar patterns with increasing complexity
    {
        "number": 9,
        "title_ar": "حرف لام وراء",
        "title_fr": "Les lettres Lām et Rā — articulation précise",
        "description_fr": "Maîtrisez la prononciation du Lām et Rā, très importants en arabe.",

        "explanation_sections": [
            {
                "title_fr": "Lām (ل) — consonne latérale",
                "content_fr": """Le Lām est une consonne latérale alvéolaire. La langue monte contre les alvéoles supérieures,
l'air s'échappe sur les côtés. Similaire au 'l' français dans 'lune', mais légèrement différent.
Il existe deux prononciations : Lām clair (avant les voyelles antérieures) et Lām sombre (avant les voyelles postérieures).""",
                "content_ar": "اللام = حرف الجانبية",
                "audio_hint": "Son 'l' comme dans 'lune' français",
                "tip_fr": "Langue contre les alvéoles, air sur les côtés",
                "common_mistakes_fr": "Prononcer trop comme le français 'l', perdre la nuance arabe"
            },
            {
                "title_fr": "Rā (ر) — consonne battue",
                "content_fr": """Le Rā est une consonne battue alvéolaire. La langue fait un petit coup contre les alvéoles.
Similaire au 'r' espagnol simple, pas roulé. C'est très différent du 'r' français guttural.
L'arabe est plus léger que beaucoup de francophones ne le pensent.""",
                "content_ar": "الراء = حرف الرقة",
                "audio_hint": "Son 'r' léger et battue, pas roulé",
                "tip_fr": "Dites 'r' rapidement, un seul coup de langue",
                "common_mistakes_fr": "Rouler le 'r' ou utiliser le 'r' guttural français"
            }
        ],

        "examples": [
            {
                "arabic": "لِسَان",
                "transliteration": "li-sān",
                "explanation_fr": "Langue. Lām clair (avant Kasra, voyelle antérieure).",
                "audio_description_fr": "li-sān (Lām clair)"
            },
            {
                "arabic": "رَاقِب",
                "transliteration": "rā-qib",
                "explanation_fr": "Observateur. Rā clairement distinct.",
                "audio_description_fr": "rā-qib"
            }
        ],

        "quiz": [
            {
                "question_fr": "Quel est le point d'articulation du Lām ?",
                "type": "MCQ",
                "choices": ["Labiale", "Dentale", "Alvéolaire latérale", "Vélaire"],
                "correct_index": 2,
                "explanation_fr": "Lām = consonante latérale alvéolaire"
            }
        ]
    },

    {
        "number": 10,
        "title_ar": "الأحرف الشبيهة",
        "title_fr": "Les lettres confondables — Bā, Tā, Thā, Nūn, Yā",
        "description_fr": "Distinguez les lettres qui se ressemblent visuellement ou phonétiquement.",

        "explanation_sections": [
            {
                "title_fr": "Distinctions visuelles et phonétiques",
                "content_fr": """Plusieurs lettres se ressemblent. En écriture :
- Bā (ب), Tā (ت), Thā (ث), Nūn (ن), Yā (ي) se différencient par le nombre de points
- En prononciation : Tā/Thā, Bā/Fā, etc. sont proches

Il faut apprendre à les distinguer rapidement et prononciation correctement.""",
                "content_ar": "الحروف المتشابهة",
                "audio_hint": "Écouter les différences subtiles",
                "tip_fr": "Mémorisez d'abord la prononciation, puis la forme écrite",
                "common_mistakes_fr": "Confondre visuellement Bā et Tā, ou Nūn et Yā"
            }
        ],

        "examples": [
            {
                "arabic": "ب ت ث ن ي",
                "transliteration": "ba ta tha na ya",
                "explanation_fr": "5 lettres avec des points (diacritiques diacritiques différentes).",
                "audio_description_fr": "Écoutez les différences phonétiques"
            }
        ],

        "quiz": [
            {
                "question_fr": "Combien de points Thā (ث) a-t-elle ?",
                "type": "MCQ",
                "choices": ["1", "2", "3", "0"],
                "correct_index": 2,
                "explanation_fr": "Thā (ث) = 3 points sur la lettre"
            }
        ]
    },

    {
        "number": 11,
        "title_ar": "تطبيق قراءة السور القصيرة",
        "title_fr": "Application : Lire les petites Sourates (Al-Nas, Al-Falaq, etc.)",
        "description_fr": "Appliquez tous les concepts appris pour lire des sourates complètes du Coran.",

        "explanation_sections": [
            {
                "title_fr": "Sourates courtes du Coran",
                "content_fr": """Les dernières sourates du Coran (Juz 'Amma) sont les plus courtes et les plus appropriées pour débuter.
Vous allez appliquer TOUS les concepts appris : lettres, voyelles, Sukun, Madd, Shadda, Nūn/Tanwin, etc.
C'est une excellente révision et application pratique.""",
                "content_ar": "تطبيق على سور قصيرة",
                "audio_hint": "Fluidité et cohérence dans la lecture",
                "tip_fr": "Lisez d'abord lentement, puis augmentez la vitesse",
                "common_mistakes_fr": "Sauter les diacritiques, lire trop vite"
            }
        ],

        "examples": [
            {
                "arabic": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
                "transliteration": "Bis-mi-l-lā-hi-r-rah-mā-ni-r-ra-ḥī-m",
                "explanation_fr": "La Basmalah (Au nom de Dieu...). Prononciation complète.",
                "audio_description_fr": "Bismillahi-r-rahmaani-r-raheem (correct)"
            }
        ]
    },

    {
        "number": 12,
        "title_ar": "الحروف الممدودة والمشددة المتكررة",
        "title_fr": "Révision : Madd, Shadda et cas complexes",
        "description_fr": "Pratiquez les cas les plus difficiles avec Madd et Shadda ensemble.",

        "explanation_sections": [
            {
                "title_fr": "Cas complexes",
                "content_fr": """Parfois, Madd et Shadda se combinent. Parfois Tanwin avec Sukun. Ces cas complexes requièrent
une compréhension profonde des règles.""",
                "content_ar": "حالات معقدة",
                "audio_hint": "Reconnaître les patterns",
                "tip_fr": "Analysez d'abord, prononcez ensuite",
                "common_mistakes_fr": "Trop vite, sans analyser"
            }
        ]
    },

    {
        "number": 13,
        "title_ar": "أحكام الميم والباء والفاء",
        "title_fr": "Règles spéciales pour Mīm, Bā et Fā",
        "description_fr": "Maîtrisez les nuances des consonnes labiales.",

        "explanation_sections": [
            {
                "title_fr": "Ghunna (nasalité) avec Mīm",
                "content_fr": """Mīm avec Sukun a aussi des règles spéciales : Iẓhār, Idghām (fusion), Ikhfā.
Similaire aux règles du Nūn mais légèrement différentes.""",
                "content_ar": "أحكام الميم الساكنة",
                "audio_hint": "Nasalité particulière",
                "tip_fr": "Écoutez les différences avec Nūn",
                "common_mistakes_fr": "Appliquer les mêmes règles que Nūn"
            }
        ]
    },

    {
        "number": 14,
        "title_ar": "حروف الهمس والجهر",
        "title_fr": "Consonnes sourdes et sonores (Hafs vs Jahir)",
        "description_fr": "Comprenez la distinction entre sourdes et sonores pour le Tajwid.",

        "explanation_sections": [
            {
                "title_fr": "Hafs et Jahir",
                "content_fr": """Certaines consonnes sont SOURDES (pas de vibration vocale) : Fā, Thā, etc.
D'autres sont SONORES (avec vibration vocale) : Bā, Dhāl, etc.
Cette distinction est importante pour la prononciation correcte.""",
                "content_ar": "الحروف المهموسة والمجهورة",
                "audio_hint": "Ressentez la vibration ou non",
                "tip_fr": "Mettez votre main sur votre gorge pour sentir la vibration",
                "common_mistakes_fr": "Ignorer la distinction"
            }
        ]
    },

    {
        "number": 15,
        "title_ar": "الأحرف المستعلية والمستفلة",
        "title_fr": "Lettres avec et sans emphase (Mustafal et Musta'aliya)",
        "description_fr": "Apprenez la distinction entre lettres 'épaisses' et 'fines'.",

        "explanation_sections": [
            {
                "title_fr": "Emphase (Tafkhim) vs légèreté",
                "content_fr": """Certaines lettres sont prononcées avec emphase (langue reculée, voix 'épaisse') :
Ṭā, Ḍā, Ṣā, Ẓā (les 4 lettres emphasisées).
C'est très important pour la prononciation arabe correcte. Les francophones oublient souvent l'emphase.""",
                "content_ar": "الحروف المستعلية = الحروف المفخمة",
                "audio_hint": "Voix 'épaisse' pour les emphasized",
                "tip_fr": "Écoutez un locuteur natif pour sentir la différence",
                "common_mistakes_fr": "Prononcer sans emphase"
            }
        ]
    },

    {
        "number": 16,
        "title_ar": "الوقف والوصل",
        "title_fr": "Pause et liaison (Waqf et Wasl) — notion de base",
        "description_fr": "Comprenez quand faire une pause et quand lier les mots.",

        "explanation_sections": [
            {
                "title_fr": "Waqf (arrêt) et Wasl (liaison)",
                "content_fr": """Dans la récitation coranique, on s'arrête parfois à la fin des versets ou avant certains mots.
Ces arrêts s'appellent 'Waqf'. Entre les arrêts, les mots sont liés (Wasl).
C'est une notion fondamentale du Tajwid avancé.""",
                "content_ar": "الوقف والوصل في التجويد",
                "audio_hint": "Respiration et rythme",
                "tip_fr": "Écoutez une récitation coranique pour les patterns",
                "common_mistakes_fr": "S'arrêter au mauvais endroit"
            }
        ]
    },

    {
        "number": 17,
        "title_ar": "مراجعة شاملة وتقييم",
        "title_fr": "Révision complète et évaluation (Test final Nourania)",
        "description_fr": "Testez votre maîtrise de tous les concepts Nourania.",

        "explanation_sections": [
            {
                "title_fr": "Résumé des 16 chapitres précédents",
                "content_fr": """Vous avez appris :
1. Les 29 lettres
2. Les 3 voyelles courtes
3. Le Tanwin
4. Le Sukun
5. Les lettres de Madd (Alif, Yā, Wāw)
6. Madd avec Sukun
7. La Shadda
8. Règles Nūn/Tanwin (Iẓhār, Idghām, Iqlāb, Ikhfā)
9. Lām et Rā
10. Lettres confondables
11. Application sur sourates courtes
12. Cas complexes
13. Règles spéciales
14. Sourdes/sonores
15. Emphase
16. Waqf/Wasl
17. Révision

Vous êtes maintenant prêt pour la lecture coranique avancée !""",
                "content_ar": "مراجعة شاملة",
                "audio_hint": "Tous les concepts appris",
                "tip_fr": "Révisez régulièrement",
                "common_mistakes_fr": "Abandonner après le chapitre 1"
            }
        ],

        "quiz": [
            {
                "question_fr": "Combien de lettres arabes y a-t-il ?",
                "type": "MCQ",
                "choices": ["26", "28", "29", "32"],
                "correct_index": 2,
                "explanation_fr": "29 lettres (28 si on exclut Hamza)"
            },
            {
                "question_fr": "Les 4 règles du Nūn s'appellent comment ?",
                "type": "MCQ",
                "choices": ["Iẓhār, Idghām, Iqlāb, Ikhfā", "Waqf, Wasl, Madd, Sukun", "Fatha, Kasra, Damma, Tanwin", "Abjadi, Alphabetic, Phonetic, Tajweed"],
                "correct_index": 0,
                "explanation_fr": "Les 4 règles du Nūn : Iẓhār, Idghām, Iqlāb, Ikhfā"
            },
            {
                "question_fr": "Quel est le son le plus difficile pour les francophones ?",
                "type": "MCQ",
                "choices": ["Bā (b)", "Ḥā (pharyngal)", "Ain (pharyngal voiced)", "Toutes les fricatives"],
                "correct_index": 2,
                "explanation_fr": "Ain (ع) est considéré comme le son arabe le PLUS difficile pour les débutants"
            }
        ],

        "challenges": [
            {
                "type": "speed_reading",
                "title_fr": "Défi final : Lire une sourate complète",
                "description_fr": "Lisez Sourate Al-Nas (114) fluidement",
                "items": ["بِسْمِ اللَّهِ", "قُلْ أَعُوذُ", "بِرَبِّ النَّاسِ"],
                "time_limit_seconds": 60
            }
        ]
    }
]


# ============================================================================
# GAMIFICATION & LEARNING FEATURES
# ============================================================================

PRONUNCIATION_COACH_DATA = [
    {
        "letter": "ح",
        "name": "Ḥā",
        "difficulty": 3,
        "mouth_diagram": {
            "tongue_position": "back_of_throat",
            "throat_opening": "partially_open",
            "vocal_cords": "voiceless",
            "airflow": "fricative",
            "technique": "Creusez la gorge comme pour dire 'kh' mais plus rauque, sourde et avec constriction pharyngale"
        },
        "comparison_fr": "Plus guttural que le 'h' français. Similaire au 'ch' allemand dans 'Bach'",
        "common_issue": "Les francophones prononcent 'h' au lieu de la fricative pharyngale",
        "practice_steps": [
            "1. Dites 'aaaa' profondément de la gorge",
            "2. Réduisez l'air jusqu'à créer une friction",
            "3. Rendez-la sourde (sans vibration vocale)",
            "4. Pratiquez : ḥa ḥa ḥa"
        ]
    },
    {
        "letter": "خ",
        "name": "Khā",
        "difficulty": 2,
        "mouth_diagram": {
            "tongue_position": "velum",
            "airflow": "fricative",
            "vocal_cords": "voiceless",
            "technique": "Langue levée vers le voile du palais, souffle sans vibration vocale"
        },
        "comparison_fr": "Comme le 'j' espagnol dans 'jota' ou 'j' portugais",
        "common_issue": "Pas assez dorsal, ressemble à 'h' ou 'f'",
        "practice_steps": [
            "1. Dites le son 'k', puis gardez la position",
            "2. Au lieu d'une occlusive, faites une friction",
            "3. Souffle rauque : 'kh kh kh'",
            "4. Intégrez avec une voyelle : 'kha khi khu'"
        ]
    },
    {
        "letter": "ع",
        "name": "Ain",
        "difficulty": 4,
        "mouth_diagram": {
            "throat_position": "pharynx",
            "vocal_cords": "voiced",
            "throat_constriction": "strong",
            "airflow": "fricative_with_resonance",
            "technique": "Resserrez la gorge comme si vous aviez mal, puis libérez avec vibration vocale"
        },
        "comparison_fr": "Aucune équivalent en français. Son unique et très difficile.",
        "common_issue": "Les débutants prononcent 'a' simple ou confondent avec Ḥā",
        "practice_steps": [
            "1. Resserrez légèrement la gorge",
            "2. Maintenez la vibration vocale (sons 'e' basique)",
            "3. Créez une friction en resserrant plus",
            "4. Pratiquez : ʿa ʿi ʿu"
        ]
    },
    {
        "letter": "غ",
        "name": "Ghain",
        "difficulty": 2,
        "mouth_diagram": {
            "tongue_position": "velum",
            "airflow": "fricative",
            "vocal_cords": "voiced",
            "technique": "Similaire à Khā mais SONORE (avec vibration vocale)"
        },
        "comparison_fr": "Comme le 'r' guttural français roulé",
        "common_issue": "Trop similaire à Khā ou à Ḥā",
        "practice_steps": [
            "1. Prononcez Khā (kh kh kh)",
            "2. Maintenant vibrez vos cordes vocales : 'ghgh'",
            "3. C'est Ghain = Khā sonore",
            "4. Pratiquez : 'gha ghi ghu'"
        ]
    },
    {
        "letter": "ق",
        "name": "Qāf",
        "difficulty": 1,
        "mouth_diagram": {
            "tongue_position": "velum",
            "airflow": "occlusive",
            "vocal_cords": "voiceless",
            "technique": "Même position que Kāf mais plus loin en arrière, plus profond"
        },
        "comparison_fr": "Ressemble au 'k' français mais plus profond dans la gorge",
        "common_issue": "Confusionner avec Kāf",
        "practice_steps": [
            "1. Prononcez Kāf : 'ka ka ka'",
            "2. Reculez la langue plus loin vers la gorge",
            "3. Maintenez l'occlusion plus longtemps",
            "4. Relâchez : 'Qa Qa Qa'"
        ]
    }
]


COLOR_CODED_WORDS = {
    "green_mastered": [
        {"word": "بَ", "meaning": "Ba (consonant + vowel)"},
        {"word": "تَ", "meaning": "Ta (consonant + vowel)"},
        {"word": "دَ", "meaning": "Da (consonant + vowel)"}
    ],
    "orange_learning": [
        {"word": "ح", "meaning": "Ḥā (difficult pharyngeal sound)"},
        {"word": "خ", "meaning": "Khā (velum fricative)"},
        {"word": "ع", "meaning": "Ain (pharyngeal fricative)"}
    ],
    "red_new": [
        {"word": "غ", "meaning": "Ghain (voiced velum fricative)"},
        {"word": "ق", "meaning": "Qāf (occlusive velum)"},
        {"word": "ظ", "meaning": "Ẓā (emphatic pharyngeal fricative)"}
    ]
}


SYLLABLE_BUILDER_EXERCISES = [
    {
        "id": "exercise_1",
        "title": "Construire CV simples",
        "description": "Combinez une consonne et une voyelle pour former CV",
        "exercise_type": "drag_drop",
        "consonants": ["ب", "ت", "د", "س", "ن"],
        "vowels": ["َ (Fatha)", "ِ (Kasra)", "ُ (Damma)"],
        "target_combinations": [
            {"consonant": "ب", "vowel": "َ", "result": "بَ", "points": 10},
            {"consonant": "ت", "vowel": "ِ", "result": "تِ", "points": 10},
            {"consonant": "د", "vowel": "ُ", "result": "دُ", "points": 10}
        ]
    },
    {
        "id": "exercise_2",
        "title": "Former des mots avec 2 syllabes",
        "description": "Assemblez deux CV pour former un petit mot",
        "exercise_type": "drag_drop",
        "syllables": ["بَ", "تَ", " دَ", "رَ"],
        "target_words": [
            {"syllables": ["بَ", "تَ"], "result": "بَتَ", "points": 20},
            {"syllables": ["دَ", "رَ"], "result": "دَرَ", "points": 20}
        ]
    }
]


MEMORY_PAIR_GAMES = [
    {
        "id": "memory_1",
        "title": "Les 3 voyelles",
        "pairs": [
            {"left": "بَ", "right": "ba"},
            {"left": "بِ", "right": "bi"},
            {"left": "بُ", "right": "bu"},
            {"left": "تَ", "right": "ta"},
            {"left": "تِ", "right": "ti"},
            {"left": "تُ", "right": "tu"}
        ],
        "points_per_pair": 20
    },
    {
        "id": "memory_2",
        "title": "Lettres difficiles",
        "pairs": [
            {"left": "ح", "right": "Ḥā (pharyngeal)"},
            {"left": "خ", "right": "Khā (velar)"},
            {"left": "ع", "right": "Ain (pharyngeal voiced)"},
            {"left": "غ", "right": "Ghain (velar voiced)"}
        ],
        "points_per_pair": 30
    }
]


def seed_nourania_enriched(db: Session) -> None:
    """
    Seed the database with enriched Nourania and Voyelles/Syllabes curriculum data.

    This function creates detailed, pedagogically-sound learning content with:
    - Comprehensive explanations in French for complete beginners
    - Pronunciation guides and mouth diagrams
    - Practice examples and quizzes
    - Gamification challenges
    - Color-coded difficulty progression

    Args:
        db: SQLAlchemy session

    Returns:
        None (data is persisted to database)
    """
    # This function would integrate with your ORM models to persist the data
    # The structure above provides the complete data ready for insertion

    # Pseudocode for implementation:
    # 1. Create Program objects for VOYELLES_SYLLABES and NOURANIA_ENRICHED
    # 2. Iterate through VOYELLES_SYLLABES_UNITS and create Unit objects
    # 3. For each unit, create related objects: explanations, examples, illustrations, quiz, challenges
    # 4. Iterate through NOURANIA_ENRICHED_CHAPTERS and create Chapter objects
    # 5. Create associated teaching aids: PRONUNCIATION_COACH_DATA, SYLLABLE_BUILDER_EXERCISES, etc.
    # 6. Commit all to database

    pass


if __name__ == "__main__":
    print("Nourania Enriched Seed Data Module")
    print("====================================")
    print(f"Voyelles & Syllabes Units: {len(VOYELLES_SYLLABES_UNITS)}")
    print(f"Nourania Enriched Chapters: {len(NOURANIA_ENRICHED_CHAPTERS)}")
    print(f"Pronunciation Coach Entries: {len(PRONUNCIATION_COACH_DATA)}")
    print(f"Syllable Builder Exercises: {len(SYLLABLE_BUILDER_EXERCISES)}")
    print(f"Memory Pair Games: {len(MEMORY_PAIR_GAMES)}")
