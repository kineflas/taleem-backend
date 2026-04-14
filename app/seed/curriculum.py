"""
Curriculum Engine seed data — 5 complete learning programs.

Run: python -m app.seed.curriculum
Called automatically on startup (idempotent).
"""
from ..database import SessionLocal
from ..models.curriculum import (
    CurriculumProgram, CurriculumUnit, CurriculumItem,
    CurriculumType, ProgramCategory, UnitType, ItemType,
)


# ══════════════════════════════════════════════════════════════════════════════
# Program 1 — Alphabet Arabe
# 28 letters × 4 positions = 112 items
# ══════════════════════════════════════════════════════════════════════════════

ARABIC_LETTERS = [
    # (number, arabic_name_fr, glyph_isolated, glyph_initial, glyph_medial, glyph_final, transliteration, description_fr)
    (1,  "Alif",   "ا", "ا", "ا", "ا",  "ā / '",  "Première lettre, elle est parfois une hamza (occlusive glottale) et parfois une voyelle longue."),
    (2,  "Bā",     "ب", "بـ", "ـبـ", "ـب", "b",    "Consonne bilabiale occlusive sonore. Se prononce comme le 'b' français."),
    (3,  "Tā",     "ت", "تـ", "ـتـ", "ـت", "t",    "Consonne dentale occlusive sourde. Se prononce comme le 't' français."),
    (4,  "Thā",    "ث", "ثـ", "ـثـ", "ـث", "th",   "Consonne dentale fricative sourde. Comme le 'th' anglais de 'think'."),
    (5,  "Jīm",    "ج", "جـ", "ـجـ", "ـج", "j",    "Consonne palatale affriquée sonore. Varie selon les dialectes (j, dj, g)."),
    (6,  "Ḥā",     "ح", "حـ", "ـحـ", "ـح", "ḥ",   "Consonne pharyngale fricative sourde. Son unique à l'arabe, produit dans le fond de la gorge."),
    (7,  "Khā",    "خ", "خـ", "ـخـ", "ـخ", "kh",   "Consonne vélaire fricative sourde. Comme le 'j' espagnol ou le 'ch' allemand de 'Bach'."),
    (8,  "Dāl",    "د", "د", "ـد", "ـد",  "d",    "Consonne dentale occlusive sonore. Se prononce comme le 'd' français."),
    (9,  "Dhāl",   "ذ", "ذ", "ـذ", "ـذ",  "dh",   "Consonne dentale fricative sonore. Comme le 'th' anglais de 'this'."),
    (10, "Rā",     "ر", "ر", "ـر", "ـر",  "r",    "Consonne alvéolaire battue ou roulée. Comme le 'r' espagnol simple."),
    (11, "Zāy",    "ز", "ز", "ـز", "ـز",  "z",    "Consonne alvéolaire fricative sonore. Comme le 'z' français."),
    (12, "Sīn",    "س", "سـ", "ـسـ", "ـس", "s",    "Consonne alvéolaire fricative sourde. Comme le 's' français."),
    (13, "Shīn",   "ش", "شـ", "ـشـ", "ـش", "sh",   "Consonne post-alvéolaire fricative sourde. Comme le 'ch' français."),
    (14, "Ṣād",    "ص", "صـ", "ـصـ", "ـص", "ṣ",   "Consonne alvéolaire fricative sourde emphatique. S avec la gorge."),
    (15, "Ḍād",    "ض", "ضـ", "ـضـ", "ـض", "ḍ",   "Consonne emphatique. L'arabe est parfois appelé 'langue du Ḍād'."),
    (16, "Ṭā",     "ط", "طـ", "ـطـ", "ـط", "ṭ",   "Consonne dentale occlusive sourde emphatique. T avec la gorge."),
    (17, "Ẓā",     "ظ", "ظـ", "ـظـ", "ـظ", "ẓ",   "Consonne dentale fricative sonore emphatique."),
    (18, "'Ayn",   "ع", "عـ", "ـعـ", "ـع", "'",    "Consonne pharyngale fricative sonore. Constriction du pharynx."),
    (19, "Ghayn",  "غ", "غـ", "ـغـ", "ـغ", "gh",   "Consonne uvulaire fricative sonore. Proche du 'r' parisien grasseyé."),
    (20, "Fā",     "ف", "فـ", "ـفـ", "ـف", "f",    "Consonne labio-dentale fricative sourde. Comme le 'f' français."),
    (21, "Qāf",    "ق", "قـ", "ـقـ", "ـق", "q",    "Consonne uvulaire occlusive sourde. K produit très en arrière."),
    (22, "Kāf",    "ك", "كـ", "ـكـ", "ـك", "k",    "Consonne vélaire occlusive sourde. Comme le 'k' français."),
    (23, "Lām",    "ل", "لـ", "ـلـ", "ـل", "l",    "Consonne alvéolaire latérale. Comme le 'l' français."),
    (24, "Mīm",    "م", "مـ", "ـمـ", "ـم", "m",    "Consonne bilabiale nasale. Comme le 'm' français."),
    (25, "Nūn",    "ن", "نـ", "ـنـ", "ـن", "n",    "Consonne alvéolaire nasale. Comme le 'n' français."),
    (26, "Hā",     "ه", "هـ", "ـهـ", "ـه", "h",    "Consonne glottale fricative sourde. H expiré, comme en anglais."),
    (27, "Wāw",    "و", "و", "ـو", "ـو",  "w / ū", "Peut être consonne (w) ou voyelle longue (ū)."),
    (28, "Yā",     "ي", "يـ", "ـيـ", "ـي", "y / ī", "Peut être consonne (y) ou voyelle longue (ī)."),
]

POSITIONS = [
    ("isolated", "Isolée",  "La lettre seule, non connectée à d'autres."),
    ("initial",  "Initiale","La lettre en début de mot, connectée à droite."),
    ("medial",   "Médiane", "La lettre au milieu du mot, connectée des deux côtés."),
    ("final",    "Finale",  "La lettre en fin de mot, connectée à gauche."),
]

GLYPHS_BY_POSITION = {
    "isolated": 2,
    "initial":  3,
    "medial":   4,
    "final":    5,
}

# Map letter name_fr → audio filename (from arabicreadingcourse.com)
LETTER_AUDIO = {
    "Alif": "alif", "Bā": "ba", "Tā": "ta", "Thā": "tha",
    "Jīm": "jiim", "Ḥā": "hha", "Khā": "kha", "Dāl": "daal",
    "Dhāl": "thaal", "Rā": "ra", "Zāy": "zay", "Sīn": "siin",
    "Shīn": "shiin", "Ṣād": "saad", "Ḍād": "daad", "Ṭā": "taa",
    "Ẓā": "thaa", "'Ayn": "ayn", "Ghayn": "ghayn", "Fā": "fa",
    "Qāf": "qaf", "Kāf": "kaf", "Lām": "lam", "Mīm": "miim",
    "Nūn": "nuun", "Hā": "ha", "Wāw": "waw", "Yā": "ya",
}


# ══════════════════════════════════════════════════════════════════════════════
# Program 2 — Qa'ida Nourania (17 chapters)
# ══════════════════════════════════════════════════════════════════════════════

NOURANIA_CHAPTERS = [
    {
        "number": 1,
        "title_ar": "الحروف المفردة",
        "title_fr": "Les lettres isolées",
        "description_fr": "Apprentissage des 29 lettres de l'alphabet dans leur forme isolée. L'élève apprend le nom de chaque lettre et sa prononciation.",
        "items": [
            {"title_ar": "أ", "title_fr": "Alif", "content_fr": "Occlusive glottale ou voyelle longue. Point d'articulation : glotte.", "transliteration": "ā / '", "type": "COMBINATION"},
            {"title_ar": "ب", "title_fr": "Bā", "content_fr": "Occlusive bilabiale sonore.", "transliteration": "b", "type": "COMBINATION"},
            {"title_ar": "ت", "title_fr": "Tā", "content_fr": "Occlusive dentale sourde.", "transliteration": "t", "type": "COMBINATION"},
            {"title_ar": "ث", "title_fr": "Thā", "content_fr": "Fricative dentale sourde. Langue entre les dents.", "transliteration": "th", "type": "COMBINATION"},
            {"title_ar": "ج", "title_fr": "Jīm", "content_fr": "Affriquée palatale sonore.", "transliteration": "j", "type": "COMBINATION"},
            {"title_ar": "ح", "title_fr": "Ḥā", "content_fr": "Fricative pharyngale sourde. Son unique à l'arabe.", "transliteration": "ḥ", "type": "COMBINATION"},
            {"title_ar": "خ", "title_fr": "Khā", "content_fr": "Fricative vélaire sourde.", "transliteration": "kh", "type": "COMBINATION"},
            {"title_ar": "د", "title_fr": "Dāl", "content_fr": "Occlusive dentale sonore.", "transliteration": "d", "type": "COMBINATION"},
            {"title_ar": "ذ", "title_fr": "Dhāl", "content_fr": "Fricative dentale sonore.", "transliteration": "dh", "type": "COMBINATION"},
            {"title_ar": "ر", "title_fr": "Rā", "content_fr": "Battue alvéolaire. Comme le r espagnol simple.", "transliteration": "r", "type": "COMBINATION"},
        ],
    },
    {
        "number": 2,
        "title_ar": "الحركات",
        "title_fr": "Les voyelles courtes (Tashkeel)",
        "description_fr": "Les trois voyelles courtes : Fatha (a), Kasra (i), Damma (u). Elles modifient la prononciation des lettres.",
        "items": [
            {"title_ar": "بَ", "title_fr": "Fatha (a)", "content_fr": "Petit trait oblique au-dessus de la lettre. Produit le son 'a' court.", "transliteration": "ba", "type": "COMBINATION"},
            {"title_ar": "بِ", "title_fr": "Kasra (i)", "content_fr": "Petit trait oblique sous la lettre. Produit le son 'i' court.", "transliteration": "bi", "type": "COMBINATION"},
            {"title_ar": "بُ", "title_fr": "Damma (u)", "content_fr": "Petit waw au-dessus de la lettre. Produit le son 'u' court.", "transliteration": "bu", "type": "COMBINATION"},
            {"title_ar": "بَا", "title_fr": "Alif madd", "content_fr": "Fatha + Alif = voyelle longue 'ā'. Durée doublée.", "transliteration": "bā", "type": "COMBINATION"},
            {"title_ar": "بِي", "title_fr": "Yā madd", "content_fr": "Kasra + Yā = voyelle longue 'ī'. Durée doublée.", "transliteration": "bī", "type": "COMBINATION"},
            {"title_ar": "بُو", "title_fr": "Wāw madd", "content_fr": "Damma + Wāw = voyelle longue 'ū'. Durée doublée.", "transliteration": "bū", "type": "COMBINATION"},
        ],
    },
    {
        "number": 3,
        "title_ar": "التنوين",
        "title_fr": "La nunation (Tanwin)",
        "description_fr": "Le Tanwin ajoute un 'n' final à la fin d'un mot indéfini. Trois formes correspondant aux trois voyelles.",
        "items": [
            {"title_ar": "بً", "title_fr": "Tanwin Fath", "content_fr": "Double Fatha → son 'an'. Souvent écrit sur Alif à la fin.", "transliteration": "ban", "type": "COMBINATION"},
            {"title_ar": "بٍ", "title_fr": "Tanwin Kasr", "content_fr": "Double Kasra → son 'in'.", "transliteration": "bin", "type": "COMBINATION"},
            {"title_ar": "بٌ", "title_fr": "Tanwin Damm", "content_fr": "Double Damma → son 'un'.", "transliteration": "bun", "type": "COMBINATION"},
            {"title_ar": "كِتَابً", "title_fr": "Exemple : Kitāban", "content_fr": "كِتَابٌ (un livre) avec Tanwin Fath devient كِتَابًا en accusatif.", "transliteration": "kitāban", "type": "EXAMPLE"},
        ],
    },
    {
        "number": 4,
        "title_ar": "السكون",
        "title_fr": "Le Sukun (consonne sans voyelle)",
        "description_fr": "Le Sukun (ْ) indique une lettre sans voyelle. La syllabe se ferme. Règles importantes pour la lecture fluide.",
        "items": [
            {"title_ar": "بْ", "title_fr": "Définition du Sukun", "content_fr": "Petit cercle vide au-dessus d'une lettre = pas de voyelle. La syllabe est fermée.", "transliteration": "b (sans voyelle)", "type": "RULE"},
            {"title_ar": "مَكْتَب", "title_fr": "Exemple : Maktab", "content_fr": "مَكْتَب : le K porte un Sukun, la syllabe 'mak' est fermée.", "transliteration": "mak-tab", "type": "EXAMPLE"},
            {"title_ar": "أَسْئِلَة", "title_fr": "Jonction de syllabes", "content_fr": "Quand une lettre à Sukun précède une lettre avec voyelle, elles se lisent ensemble.", "transliteration": "as-'i-la", "type": "RULE"},
        ],
    },
    {
        "number": 5,
        "title_ar": "حروف المد",
        "title_fr": "Les lettres de prolongation (Madd)",
        "description_fr": "Alif, Wāw et Yā peuvent prolonger une voyelle. Règle fondamentale du Tajwid : durée = 2 temps (Madd Tabī'ī).",
        "items": [
            {"title_ar": "آ / بَا", "title_fr": "Madd Alif (ā)", "content_fr": "Fatha + Alif sans Hamza → voyelle longue 'ā' = 2 temps.", "transliteration": "ā (2 temps)", "type": "RULE"},
            {"title_ar": "بِي", "title_fr": "Madd Yā (ī)", "content_fr": "Kasra + Yā sans points → voyelle longue 'ī' = 2 temps.", "transliteration": "ī (2 temps)", "type": "RULE"},
            {"title_ar": "بُو", "title_fr": "Madd Wāw (ū)", "content_fr": "Damma + Wāw → voyelle longue 'ū' = 2 temps.", "transliteration": "ū (2 temps)", "type": "RULE"},
            {"title_ar": "قَالَ", "title_fr": "Exemple : Qāla", "content_fr": "قَالَ (il dit) : l'Alif après le Qāf prolonge la Fatha = 2 temps.", "transliteration": "qā-la", "type": "EXAMPLE"},
        ],
    },
    {
        "number": 6,
        "title_ar": "حروف المد مع السكون",
        "title_fr": "Madd avec Sukun (Madd Lāzim)",
        "description_fr": "Quand une lettre de prolongation est suivie d'une lettre avec Sukun dans le même mot, le Madd devient obligatoire et long : 6 temps.",
        "items": [
            {"title_ar": "دَابَّة", "title_fr": "Madd Lāzim Muttasil", "content_fr": "Madd suivi de Shadda → 6 temps obligatoires.", "transliteration": "dāb-ba", "type": "RULE"},
            {"title_ar": "الضَّالِّين", "title_fr": "Exemple coranique", "content_fr": "الضَّالِّين : le Alif du Madd suivi du Lām Shadda → 6 temps.", "transliteration": "aḍ-ḍāl-lī-na", "type": "EXAMPLE"},
        ],
    },
    {
        "number": 7,
        "title_ar": "الحروف المشددة",
        "title_fr": "La Shadda (consonne doublée)",
        "description_fr": "La Shadda (ّ) indique qu'une consonne est prononcée doublement : d'abord avec Sukun, puis avec sa voyelle.",
        "items": [
            {"title_ar": "بّ", "title_fr": "Définition de la Shadda", "content_fr": "La lettre avec Shadda est prononcée deux fois : une fois fermée, une fois ouverte.", "transliteration": "bb", "type": "RULE"},
            {"title_ar": "مَدَّ", "title_fr": "Exemple : Madda", "content_fr": "مَدَّ : le Dāl est doublé. Se lit ma + dda.", "transliteration": "mad-da", "type": "EXAMPLE"},
            {"title_ar": "إِنَّ", "title_fr": "Exemple coranique : Inna", "content_fr": "إِنَّ : le Nūn est doublé. Très fréquent dans le Coran.", "transliteration": "in-na", "type": "EXAMPLE"},
        ],
    },
    {
        "number": 8,
        "title_ar": "نون التنوين والنون الساكنة",
        "title_fr": "Nūn Sākina et Tanwin — les 4 règles",
        "description_fr": "Quand un Nūn sans voyelle (ou Tanwin) est suivi d'une autre lettre, quatre règles s'appliquent selon la lettre suivante.",
        "items": [
            {"title_ar": "إِظْهَار", "title_fr": "Règle 1 : Iẓhār (clarté)", "content_fr": "Devant ء ه ع ح غ خ : le Nūn se prononce clairement, sans aucune nasalisation.", "transliteration": "iẓ-hār", "type": "RULE", "metadata": {"letters": ["ء", "ه", "ع", "ح", "غ", "خ"]}},
            {"title_ar": "إِدْغَام", "title_fr": "Règle 2 : Idghām (fusion)", "content_fr": "Devant ي ر م ل و ن : le Nūn se fusionne avec la lettre suivante. Avec et sans Ghunna.", "transliteration": "id-ghām", "type": "RULE", "metadata": {"letters": ["ي", "ر", "م", "ل", "و", "ن"]}},
            {"title_ar": "إِقْلَاب", "title_fr": "Règle 3 : Iqlāb (transformation)", "content_fr": "Devant ب uniquement : le Nūn se transforme en Mīm avec nasalisation.", "transliteration": "iq-lāb", "type": "RULE", "metadata": {"letters": ["ب"]}},
            {"title_ar": "إِخْفَاء", "title_fr": "Règle 4 : Ikhfā (dissimulation)", "content_fr": "Devant les 15 lettres restantes : le Nūn est caché avec nasalisation entre Iẓhār et Idghām.", "transliteration": "ikh-fā", "type": "RULE"},
        ],
    },
    {
        "number": 9,
        "title_ar": "الميم الساكنة",
        "title_fr": "Mīm Sākina — 3 règles",
        "description_fr": "Quand un Mīm sans voyelle est suivi d'une lettre, trois règles s'appliquent.",
        "items": [
            {"title_ar": "إِخْفَاء شَفَوِي", "title_fr": "Ikhfā Shafawī", "content_fr": "Devant ب : le Mīm est dissimulé avec nasalisation.", "transliteration": "ikhfā shafawī", "type": "RULE"},
            {"title_ar": "إِدْغَام شَفَوِي", "title_fr": "Idghām Shafawī", "content_fr": "Devant م : le Mīm se fusionne avec le Mīm suivant.", "transliteration": "idghām shafawī", "type": "RULE"},
            {"title_ar": "إِظْهَار شَفَوِي", "title_fr": "Iẓhār Shafawī", "content_fr": "Devant toutes les autres lettres : le Mīm se prononce clairement.", "transliteration": "iẓhār shafawī", "type": "RULE"},
        ],
    },
    {
        "number": 10,
        "title_ar": "لام التعريف",
        "title_fr": "Le Lām de la définition (Al-)",
        "description_fr": "L'article défini 'Al-' (ال) : le Lām se prononce ou se fond selon la lettre suivante.",
        "items": [
            {"title_ar": "اللَّام الشَّمْسِيَّة", "title_fr": "Lām Shamsiyya (lettres solaires)", "content_fr": "Devant 14 lettres dites 'solaires', le Lām se fusionne : الشَّمْس → ash-shams.", "transliteration": "ash-shams", "type": "RULE", "metadata": {"letters": ["ت","ث","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ","ل","ن"]}},
            {"title_ar": "اللَّام الْقَمَرِيَّة", "title_fr": "Lām Qamariyya (lettres lunaires)", "content_fr": "Devant les 14 lettres 'lunaires', le Lām se prononce clairement : الْقَمَر → al-qamar.", "transliteration": "al-qamar", "type": "RULE"},
        ],
    },
    {
        "number": 11,
        "title_ar": "مخارج الحروف",
        "title_fr": "Les points d'articulation (Makhārij)",
        "description_fr": "L'arabophone prononce chaque lettre depuis un point précis. Il y a 17 points principaux répartis en 5 zones.",
        "items": [
            {"title_ar": "الجَوْف", "title_fr": "Zone 1 : Cavité buccale (Jawf)", "content_fr": "Les 3 lettres de prolongation : ا و ي. Prononcées avec l'air dans la bouche.", "transliteration": "jawf", "type": "RULE"},
            {"title_ar": "الحَلْق", "title_fr": "Zone 2 : Gorge (Ḥalq)", "content_fr": "6 lettres : ء ه ع ح غ خ. Trois points dans la gorge.", "transliteration": "ḥalq", "type": "RULE"},
            {"title_ar": "اللِّسَان", "title_fr": "Zone 3 : Langue (Lisān)", "content_fr": "18 lettres produites par différentes parties de la langue.", "transliteration": "lisān", "type": "RULE"},
            {"title_ar": "الشَّفَتَان", "title_fr": "Zone 4 : Lèvres (Shafatān)", "content_fr": "4 lettres labiales : ب م و ف.", "transliteration": "shafatān", "type": "RULE"},
            {"title_ar": "الخَيْشُوم", "title_fr": "Zone 5 : Fosse nasale (Khayshūm)", "content_fr": "Le Ghunna (nasalisation) produit dans les fosses nasales.", "transliteration": "khayshūm", "type": "RULE"},
        ],
    },
    {
        "number": 12,
        "title_ar": "صفات الحروف",
        "title_fr": "Caractéristiques des lettres (Sifāt)",
        "description_fr": "Chaque lettre possède des attributs phonétiques permanents (Sifāt Lāzima) et variables (Sifāt 'Āriḍa).",
        "items": [
            {"title_ar": "الجَهْر / الهَمْس", "title_fr": "Sonorité : Sonore vs. Sourd", "content_fr": "الجَهْر : lettres sonores (corde vocale vibre). الهَمْس : lettres sourdes (souffle seul).", "transliteration": "jahr / hams", "type": "RULE"},
            {"title_ar": "الشِّدَّة / الرَّخَاوَة", "title_fr": "Mode : Occlusif vs. Fricatif", "content_fr": "الشِّدَّة : son bloqué puis relâché. الرَّخَاوَة : son continu.", "transliteration": "shidda / rakhāwa", "type": "RULE"},
            {"title_ar": "الاسْتِعْلَاء / الاسْتِفَال", "title_fr": "Hauteur : Élevé vs. Bas", "content_fr": "الاسْتِعْلَاء : lettres emphatiques, langue monte. Les 7 lettres : خ ص ض ط ظ غ ق.", "transliteration": "isti'lā / istifāl", "type": "RULE"},
        ],
    },
    {
        "number": 13,
        "title_ar": "المد وأنواعه",
        "title_fr": "Le Madd — types et durées",
        "description_fr": "Le Madd (prolongation) varie de 2 à 6 temps selon le contexte. Connaissance indispensable pour une récitation correcte.",
        "items": [
            {"title_ar": "مَدٌّ طَبِيعِي", "title_fr": "Madd Ṭabī'ī (2 temps)", "content_fr": "Le Madd naturel : lettre de prolongation sans cause. Durée : 2 temps (harakat).", "transliteration": "2 temps", "type": "RULE"},
            {"title_ar": "مَدٌّ مُتَّصِل", "title_fr": "Madd Muttaṣil (4-5 temps)", "content_fr": "Lettre de Madd + Hamza dans le MÊME mot. Durée : 4 ou 5 temps.", "transliteration": "4-5 temps", "type": "RULE"},
            {"title_ar": "مَدٌّ مُنْفَصِل", "title_fr": "Madd Munfaṣil (2-5 temps)", "content_fr": "Lettre de Madd en fin de mot + Hamza au début du mot suivant. Variable selon la qirā'a.", "transliteration": "2-5 temps", "type": "RULE"},
            {"title_ar": "مَدٌّ لَازِم", "title_fr": "Madd Lāzim (6 temps)", "content_fr": "Lettre de Madd + Sukun ou Shadda permanent. Durée obligatoire : 6 temps.", "transliteration": "6 temps", "type": "RULE"},
        ],
    },
    {
        "number": 14,
        "title_ar": "الوقف والابتداء",
        "title_fr": "Le Waqf (pause) et l'Ibtidā (reprise)",
        "description_fr": "Savoir où s'arrêter et reprendre dans la récitation. Les signes de Waqf dans le Mushaf guident le lecteur.",
        "items": [
            {"title_ar": "وَقْف تَامّ (م)", "title_fr": "Waqf Tāmm — Arrêt obligatoire", "content_fr": "Signe م (Lāzim) : arrêt obligatoire. Sens complet, pas de lien grammatical avec la suite.", "transliteration": "m = lāzim", "type": "RULE"},
            {"title_ar": "وَقْف جَائِز (ج)", "title_fr": "Waqf Jā'iz — Arrêt autorisé", "content_fr": "Signe ج : arrêt autorisé mais le sens continue.", "transliteration": "j = jā'iz", "type": "RULE"},
            {"title_ar": "وَقْف مَمْنُوع (لا)", "title_fr": "Waqf Mamnū' — Arrêt interdit", "content_fr": "Signe لا : ne pas s'arrêter ici. Fausserait le sens.", "transliteration": "lā = interdit", "type": "RULE"},
        ],
    },
    {
        "number": 15,
        "title_ar": "الهمزة وأنواعها",
        "title_fr": "La Hamza — formes et règles",
        "description_fr": "La Hamza (occlusive glottale) peut s'écrire sur Alif, Wāw, Yā ou seule. Règles orthographiques strictes.",
        "items": [
            {"title_ar": "أ / إ", "title_fr": "Hamza sur Alif", "content_fr": "Hamza en début de mot sur Alif : أ (avec Fatha/Damma) ou إ (avec Kasra).", "type": "RULE"},
            {"title_ar": "ؤ", "title_fr": "Hamza sur Wāw", "content_fr": "Hamza précédée ou suivie d'un 'u' long.", "type": "RULE"},
            {"title_ar": "ئ", "title_fr": "Hamza sur Yā", "content_fr": "Hamza précédée ou suivie d'un 'i' long.", "type": "RULE"},
            {"title_ar": "ء", "title_fr": "Hamza isolée", "content_fr": "Hamza en fin de mot après voyelle longue.", "type": "RULE"},
        ],
    },
    {
        "number": 16,
        "title_ar": "الحروف المتشابهة",
        "title_fr": "Lettres similaires — différentiation",
        "description_fr": "Certaines lettres ne se distinguent que par leurs points (i'jām). Exercice de discrimination visuelle et auditive.",
        "items": [
            {"title_ar": "ب / ت / ث", "title_fr": "Groupe Bā/Tā/Thā", "content_fr": "Même forme de base. 1 point dessous = Bā, 2 points dessus = Tā, 3 points dessus = Thā.", "type": "RULE"},
            {"title_ar": "ج / ح / خ", "title_fr": "Groupe Jīm/Ḥā/Khā", "content_fr": "Même forme. Point au milieu dessous = Jīm, sans point = Ḥā, point dessus = Khā.", "type": "RULE"},
            {"title_ar": "د / ذ", "title_fr": "Groupe Dāl/Dhāl", "content_fr": "Sans point = Dāl, avec un point dessus = Dhāl.", "type": "RULE"},
            {"title_ar": "س / ش", "title_fr": "Groupe Sīn/Shīn", "content_fr": "Sans points = Sīn, trois points dessus = Shīn.", "type": "RULE"},
            {"title_ar": "ص / ض", "title_fr": "Groupe Ṣād/Ḍād", "content_fr": "Sans point = Ṣād, avec point = Ḍād. Sons emphatiques distincts.", "type": "RULE"},
        ],
    },
    {
        "number": 17,
        "title_ar": "مراجعة شاملة",
        "title_fr": "Révision générale et évaluation",
        "description_fr": "Récapitulatif de tous les chapitres précédents. L'élève doit être capable de lire tout texte court avec Tashkeel.",
        "items": [
            {"title_ar": "قُلْ هُوَ اللَّهُ أَحَدٌ", "title_fr": "Récitation Al-Ikhlāṣ", "content_fr": "Sūrat Al-Ikhlāṣ : courte sourate idéale pour évaluer la lecture complète avec toutes les règles.", "transliteration": "qul huwa llāhu aḥad", "type": "EXAMPLE"},
            {"title_ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", "title_fr": "Basmala", "content_fr": "La Basmala contient : Lām Shamsiyya (الرَّحْمَٰن), Madd naturel (حِيم), Tanwin (pas ici). Exercice complet.", "transliteration": "bismi llāhi r-raḥmāni r-raḥīm", "type": "EXAMPLE"},
            {"title_ar": "اختبار شفهي", "title_fr": "Évaluation orale", "content_fr": "L'enseignant fait lire à l'élève un passage au choix. L'élève doit identifier les règles appliquées.", "type": "RULE"},
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# Program 3 — Médine Tome 1 (23 leçons)
# ══════════════════════════════════════════════════════════════════════════════

MEDINE_T1_LESSONS = [
    {
        "number": 1, "title_ar": "الدَّرْسُ الأَوَّل", "title_fr": "Leçon 1 — Noms et pronom هَذَا",
        "description_fr": "Introduction aux noms masculins et féminins. Le pronom démonstratif هَذَا (ceci/voici, masc.) et هَذِهِ (fém.).",
        "grammar": "هَذَا + nom masculin : هَذَا بَابٌ (C'est une porte).\nهَذِهِ + nom féminin : هَذِهِ نَافِذَةٌ (C'est une fenêtre).",
        "vocab": [("بَابٌ", "une porte", "bābun"), ("كِتَابٌ", "un livre", "kitābun"), ("قَلَمٌ", "un crayon", "qalamun"), ("مَكْتَبٌ", "un bureau", "maktabun"), ("نَافِذَةٌ", "une fenêtre", "nāfidhah"), ("كُرْسِيٌّ", "une chaise", "kursiyyun"), ("مِصْبَاحٌ", "une lampe", "miṣbāḥun")],
    },
    {
        "number": 2, "title_ar": "الدَّرْسُ الثَّانِي", "title_fr": "Leçon 2 — Questions : مَا هَذَا ؟",
        "description_fr": "Poser des questions avec مَا (Qu'est-ce que ?) et les réponses avec هَذَا/هَذِهِ.",
        "grammar": "مَا هَذَا ؟ → هَذَا قَلَمٌ (C'est un crayon)\nمَا هَذِهِ ؟ → هَذِهِ حَقِيبَةٌ (C'est un sac)",
        "vocab": [("حَقِيبَةٌ", "un sac", "ḥaqībah"), ("سَاعَةٌ", "une montre / horloge", "sā'ah"), ("مِفْتَاحٌ", "une clé", "miftāḥ"), ("وَرَقَةٌ", "une feuille", "waraqah"), ("سَبُّورَةٌ", "un tableau", "sabbūrah")],
    },
    {
        "number": 3, "title_ar": "الدَّرْسُ الثَّالِث", "title_fr": "Leçon 3 — Article défini ال",
        "description_fr": "L'article défini ال (al-). Distinction entre Lām Shamsiyya et Qamariyya. Concept de défini/indéfini (Tanwin).",
        "grammar": "Indéfini : بَابٌ (une porte) → Défini : الْبَابُ (la porte)\nLām solaire : الشَّمْسُ → ash-shams\nLām lunaire : الْقَمَرُ → al-qamar",
        "vocab": [("الْبَابُ", "la porte", "al-bāb"), ("الْكِتَابُ", "le livre", "al-kitāb"), ("الشَّمْسُ", "le soleil", "ash-shams"), ("الْقَمَرُ", "la lune", "al-qamar"), ("الدَّرْسُ", "la leçon", "ad-dars")],
    },
    {
        "number": 4, "title_ar": "الدَّرْسُ الرَّابِع", "title_fr": "Leçon 4 — Pronoms personnels",
        "description_fr": "Les pronoms personnels arabes : singulier, duel, pluriel. Genre masculin et féminin.",
        "grammar": "أَنَا (je) / أَنْتَ (tu, masc.) / أَنْتِ (tu, fém.)\nهُوَ (il) / هِيَ (elle)\nنَحْنُ (nous) / أَنْتُمْ (vous) / هُمْ (ils)",
        "vocab": [("أَنَا", "je / moi", "anā"), ("أَنْتَ", "tu (masc.)", "anta"), ("أَنْتِ", "tu (fém.)", "anti"), ("هُوَ", "il", "huwa"), ("هِيَ", "elle", "hiya"), ("نَحْنُ", "nous", "naḥnu")],
    },
    {
        "number": 5, "title_ar": "الدَّرْسُ الْخَامِس", "title_fr": "Leçon 5 — Professions et identité",
        "description_fr": "Exprimer sa profession. La phrase nominale sans verbe 'être' en arabe. Accord masculin/féminin.",
        "grammar": "هَذَا مُدَرِّسٌ (C'est un professeur)\nهَذِهِ مُدَرِّسَةٌ (C'est une professeure)\nأَنَا طَالِبٌ / طَالِبَةٌ (Je suis étudiant(e))",
        "vocab": [("مُدَرِّسٌ", "professeur (m)", "mudarris"), ("مُدَرِّسَةٌ", "professeure (f)", "mudarrisah"), ("طَالِبٌ", "étudiant", "ṭālib"), ("طَالِبَةٌ", "étudiante", "ṭālibah"), ("طَبِيبٌ", "médecin (m)", "ṭabīb"), ("مُهَنْدِسٌ", "ingénieur", "muhandis")],
    },
    {
        "number": 6, "title_ar": "الدَّرْسُ السَّادِس", "title_fr": "Leçon 6 — Nationalités et origines",
        "description_fr": "Demander et indiquer l'origine. Formation des adjectifs de nationalité. La question مِنْ أَيْنَ ؟",
        "grammar": "مِنْ أَيْنَ أَنْتَ ؟ → أَنَا مِنَ الْمَغْرِب (D'où es-tu ? Je suis du Maroc)\nNationalité : مَغْرِبِيٌّ (Marocain) / عَرَبِيٌّ (Arabe) / فَرَنْسِيٌّ (Français)",
        "vocab": [("مِنْ أَيْنَ", "d'où", "min ayna"), ("الْمَغْرِبُ", "le Maroc", "al-maghrib"), ("مِصْرُ", "l'Égypte", "miṣr"), ("السُّودَانُ", "le Soudan", "as-sūdān"), ("فَرَنْسَا", "la France", "faransā"), ("عَرَبِيٌّ", "arabe", "'arabī")],
    },
    {
        "number": 7, "title_ar": "الدَّرْسُ السَّابِع", "title_fr": "Leçon 7 — La famille",
        "description_fr": "Vocabulaire de la famille. Possessifs suffixes : -ي (mon/ma), -كَ (ton/ta masc.), -كِ (ton/ta fém.).",
        "grammar": "أَبِي (mon père) / أُمِّي (ma mère) / أَخِي (mon frère)\nSuffixe -كَ (ton, masc.) : أَبُوكَ (ton père)",
        "vocab": [("أَبٌ / أَبُو", "père", "ab"), ("أُمٌّ", "mère", "umm"), ("أَخٌ", "frère", "akh"), ("أُخْتٌ", "sœur", "ukht"), ("ابْنٌ", "fils", "ibn"), ("بِنْتٌ", "fille", "bint"), ("زَوْجٌ", "mari", "zawj"), ("زَوْجَةٌ", "femme", "zawjah")],
    },
    {
        "number": 8, "title_ar": "الدَّرْسُ الثَّامِن", "title_fr": "Leçon 8 — Les nombres 1 à 10",
        "description_fr": "Les chiffres arabes de 1 à 10. Accord du nombre avec le nom (inverse du français).",
        "grammar": "En arabe, le nombre de 3 à 10 s'accorde à l'inverse du nom :\nثَلَاثَةُ كُتُبٍ (3 livres, ث fém. + كتب masc.)\nثَلَاثُ بَنَاتٍ (3 filles, ث sans ة + بنات fém.)",
        "vocab": [("وَاحِدٌ", "1 — un", "wāḥid"), ("اثْنَانِ", "2 — deux", "ithnān"), ("ثَلَاثَةٌ", "3 — trois", "thalāthah"), ("أَرْبَعَةٌ", "4 — quatre", "'arba'ah"), ("خَمْسَةٌ", "5 — cinq", "khamsah"), ("سِتَّةٌ", "6 — six", "sittah"), ("سَبْعَةٌ", "7 — sept", "sab'ah"), ("ثَمَانِيَةٌ", "8 — huit", "thamāniyah"), ("تِسْعَةٌ", "9 — neuf", "tis'ah"), ("عَشَرَةٌ", "10 — dix", "'asharah")],
    },
    {
        "number": 9, "title_ar": "الدَّرْسُ التَّاسِع", "title_fr": "Leçon 9 — Couleurs et descriptions",
        "description_fr": "Les adjectifs de couleur. Accord en genre. La phrase descriptive avec accord sujet-adjectif.",
        "grammar": "L'adjectif suit le nom et s'accorde :\nالْكِتَابُ الْأَبْيَضُ (le livre blanc)\nالسَّيَّارَةُ الْبَيْضَاءُ (la voiture blanche — forme féminine)",
        "vocab": [("أَبْيَضُ / بَيْضَاءُ", "blanc/blanche", "abyaḍ/bayḍā"), ("أَسْوَدُ / سَوْدَاءُ", "noir/noire", "aswad/sawdā"), ("أَحْمَرُ / حَمْرَاءُ", "rouge", "aḥmar/ḥamrā"), ("أَخْضَرُ / خَضْرَاءُ", "vert/verte", "akhḍar/khaḍrā"), ("أَزْرَقُ / زَرْقَاءُ", "bleu/bleue", "azraq/zarqā"), ("أَصْفَرُ / صَفْرَاءُ", "jaune", "aṣfar/ṣafrā")],
    },
    {
        "number": 10, "title_ar": "الدَّرْسُ الْعَاشِر", "title_fr": "Leçon 10 — Le verbe au passé (Māḍī)",
        "description_fr": "Introduction au verbe arabe. Le passé (Māḍī) comme forme de base. Conjugaison à la 3ème personne.",
        "grammar": "Radical de base (3 lettres) : كَتَبَ (il a écrit)\nConjugaison passé :\nهُوَ كَتَبَ / هِيَ كَتَبَتْ / هُمْ كَتَبُوا",
        "vocab": [("كَتَبَ", "il a écrit", "kataba"), ("قَرَأَ", "il a lu", "qara'a"), ("ذَهَبَ", "il est allé", "dhahaba"), ("جَلَسَ", "il s'est assis", "jalasa"), ("أَكَلَ", "il a mangé", "akala"), ("شَرِبَ", "il a bu", "shariba"), ("فَتَحَ", "il a ouvert", "fataḥa")],
    },
    {
        "number": 11, "title_ar": "الدَّرْسُ الْحَادِي عَشَر", "title_fr": "Leçon 11 — Le verbe au présent (Muḍāri')",
        "description_fr": "Le présent-futur arabe (Muḍāri'). Préfixes de conjugaison. Différence passé/présent.",
        "grammar": "Présent : préfixe + radical + suffixe\nيَكْتُبُ (il écrit) / تَكْتُبُ (elle écrit / tu écris masc.)\nيَكْتُبُونَ (ils écrivent) / يَكْتُبْنَ (elles écrivent)",
        "vocab": [("يَكْتُبُ", "il écrit", "yaktub"), ("يَقْرَأُ", "il lit", "yaqra'"), ("يَذْهَبُ", "il va", "yadh-hab"), ("يَأْكُلُ", "il mange", "ya'kul"), ("يَشْرَبُ", "il boit", "yashrab"), ("يَدْرُسُ", "il étudie", "yadrus")],
    },
    {
        "number": 12, "title_ar": "الدَّرْسُ الثَّانِي عَشَر", "title_fr": "Leçon 12 — Prépositions de lieu",
        "description_fr": "Prépositions indiquant la position dans l'espace.",
        "grammar": "فِي (dans) / عَلَى (sur) / تَحْتَ (sous) / فَوْقَ (au-dessus de)\nأَمَامَ (devant) / خَلْفَ (derrière) / بَيْنَ (entre)",
        "vocab": [("فِي", "dans / à", "fī"), ("عَلَى", "sur", "'alā"), ("تَحْتَ", "sous", "taḥta"), ("فَوْقَ", "au-dessus de", "fawqa"), ("أَمَامَ", "devant", "amāma"), ("خَلْفَ", "derrière", "khalfa"), ("بَيْنَ", "entre", "bayna"), ("بِجَانِبِ", "à côté de", "bijānib")],
    },
    {
        "number": 13, "title_ar": "الدَّرْسُ الثَّالِث عَشَر", "title_fr": "Leçon 13 — Le corps humain",
        "description_fr": "Vocabulaire du corps humain. Les duals arabes (parties du corps par paires).",
        "grammar": "Le duel se forme avec le suffixe ـَانِ (nominatif) ou ـَيْنِ (cas oblique) :\nيَدٌ (une main) → يَدَانِ (deux mains) → يَدَيْنِ (des deux mains)",
        "vocab": [("رَأْسٌ", "tête", "ra's"), ("عَيْنٌ / عَيْنَانِ", "œil / deux yeux", "'ayn"), ("أُذُنٌ / أُذُنَانِ", "oreille / deux oreilles", "udhun"), ("يَدٌ / يَدَانِ", "main / deux mains", "yad"), ("رِجْلٌ / رِجْلَانِ", "pied / deux pieds", "rijl"), ("قَلْبٌ", "cœur", "qalb"), ("لِسَانٌ", "langue", "lisān")],
    },
    {
        "number": 14, "title_ar": "الدَّرْسُ الرَّابِع عَشَر", "title_fr": "Leçon 14 — La nourriture et les repas",
        "description_fr": "Vocabulaire de la nourriture. Exprimer ses préférences. Le verbe أَحَبَّ (aimer).",
        "grammar": "أُحِبُّ (j'aime) + nom défini : أُحِبُّ الْخُبْزَ (j'aime le pain)\nلَا أُحِبُّ (je n'aime pas) + nom",
        "vocab": [("خُبْزٌ", "pain", "khubz"), ("مَاءٌ", "eau", "mā'"), ("لَحْمٌ", "viande", "laḥm"), ("أَرُزٌّ", "riz", "aruzz"), ("خُضَرٌ", "légumes", "khuḍar"), ("فَاكِهَةٌ", "fruit", "fākihah"), ("حَلِيبٌ", "lait", "ḥalīb"), ("تَمْرٌ", "dattes", "tamr")],
    },
    {
        "number": 15, "title_ar": "الدَّرْسُ الْخَامِس عَشَر", "title_fr": "Leçon 15 — La prière et les ablutions",
        "description_fr": "Vocabulaire de la prière islamique. Les 5 prières quotidiennes. Verbes liés aux ablutions.",
        "grammar": "Les 5 prières + leur heure : صُبْحٌ ظُهْرٌ عَصْرٌ مَغْرِبٌ عِشَاءٌ\nتَوَضَّأَ (il a fait les ablutions) — verbe de forme V",
        "vocab": [("صَلَاةٌ", "prière", "ṣalāh"), ("وُضُوءٌ", "ablutions", "wuḍū'"), ("مَسْجِدٌ", "mosquée", "masjid"), ("أَذَانٌ", "appel à la prière", "adhān"), ("رَكْعَةٌ", "rak'a (unité de prière)", "rak'ah"), ("صَوْمٌ", "jeûne", "ṣawm"), ("زَكَاةٌ", "aumône légale", "zakāh")],
    },
    {
        "number": 16, "title_ar": "الدَّرْسُ السَّادِس عَشَر", "title_fr": "Leçon 16 — Le singulier, le duel et le pluriel",
        "description_fr": "Les 3 nombres grammaticaux arabes. Pluriels sains (réguliers) et brisés (irréguliers).",
        "grammar": "Pluriel masculin sain : مُدَرِّسُونَ (professeurs)\nPluriel féminin sain : مُدَرِّسَاتٌ (professeures)\nPluriel brisé (irrégulier) : كِتَابٌ → كُتُبٌ (livres)",
        "vocab": [("كِتَابٌ → كُتُبٌ", "livre → livres", "kitāb → kutub"), ("بَيْتٌ → بُيُوتٌ", "maison → maisons", "bayt → buyūt"), ("وَلَدٌ → أَوْلَادٌ", "garçon → garçons", "walad → awlād"), ("رَجُلٌ → رِجَالٌ", "homme → hommes", "rajul → rijāl")],
    },
    {
        "number": 17, "title_ar": "الدَّرْسُ السَّابِع عَشَر", "title_fr": "Leçon 17 — La négation",
        "description_fr": "Les particules de négation : لَا, لَيْسَ, لَمْ, لَنْ selon le contexte.",
        "grammar": "Phrase nominale : لَيْسَ هَذَا كِتَابًا (Ce n'est pas un livre)\nPrésent : لَا يَكْتُبُ (Il n'écrit pas)\nPassé négatif : لَمْ يَكْتُبْ (Il n'a pas écrit — Jussif)\nFutur négatif : لَنْ يَكْتُبَ (Il n'écrira pas — Subjonctif)",
        "vocab": [("لَا", "non / ne...pas", "lā"), ("لَيْسَ", "il n'est pas (négation nominale)", "laysa"), ("لَمْ", "ne...pas (passé)", "lam"), ("لَنْ", "ne...pas (futur)", "lan"), ("مَا", "ne...pas (autre négation)", "mā")],
    },
    {
        "number": 18, "title_ar": "الدَّرْسُ الثَّامِن عَشَر", "title_fr": "Leçon 18 — Le genre et l'accord",
        "description_fr": "Règles d'accord en genre. Le Tā Marbūṭa (ة) marque du féminin. Exceptions.",
        "grammar": "Féminin = masculin + ة : مُدَرِّسٌ → مُدَرِّسَةٌ\nExceptions féminines sans ة : أُمٌّ (mère), نَارٌ (feu), شَمْسٌ (soleil), أَرْضٌ (terre)\nFéminins anatomiques : يَدٌ (main), عَيْنٌ (œil)",
        "vocab": [("ة (تَاءُ مَرْبُوطَة)", "marque du féminin", "tā' marbūṭah"), ("مُؤَنَّثٌ", "féminin", "mu'annath"), ("مُذَكَّرٌ", "masculin", "mudhakkar")],
    },
    {
        "number": 19, "title_ar": "الدَّرْسُ التَّاسِع عَشَر", "title_fr": "Leçon 19 — Les jours de la semaine",
        "description_fr": "Les 7 jours de la semaine. Les questions de temps : مَتَى ؟ (quand ?), أَيُّ يَوْمٍ ؟ (quel jour ?).",
        "grammar": "أَيُّ يَوْمٍ هَذَا ؟ → هَذَا يَوْمُ الاثْنَيْنِ (Quel jour est-ce ? C'est lundi.)",
        "vocab": [("الأَحَدُ", "dimanche", "al-aḥad"), ("الاثْنَيْنِ", "lundi", "al-ithnayn"), ("الثُّلَاثَاءُ", "mardi", "ath-thulāthā"), ("الأَرْبِعَاءُ", "mercredi", "al-arbi'ā"), ("الْخَمِيسُ", "jeudi", "al-khamīs"), ("الْجُمُعَةُ", "vendredi", "al-jumu'ah"), ("السَّبْتُ", "samedi", "as-sabt")],
    },
    {
        "number": 20, "title_ar": "الدَّرْسُ الْعِشْرُونَ", "title_fr": "Leçon 20 — Les mois et les saisons",
        "description_fr": "Les mois hégirien et grégorien. Les 4 saisons. Expressions temporelles courantes.",
        "grammar": "Mois hégirien : مُحَرَّمٌ، صَفَرٌ، رَبِيعٌ الأَوَّلُ...\nSaisons : الرَّبِيعُ (printemps) / الصَّيْفُ (été) / الْخَرِيفُ (automne) / الشِّتَاءُ (hiver)",
        "vocab": [("شَهْرٌ", "mois", "shahr"), ("سَنَةٌ", "année", "sanah"), ("رَبِيعٌ", "printemps", "rabī'"), ("صَيْفٌ", "été", "ṣayf"), ("خَرِيفٌ", "automne", "kharīf"), ("شِتَاءٌ", "hiver", "shitā'"), ("رَمَضَانُ", "Ramadan", "ramaḍān")],
    },
    {
        "number": 21, "title_ar": "الدَّرْسُ الْحَادِي وَالْعِشْرُونَ", "title_fr": "Leçon 21 — La construction possessive (Iḍāfa)",
        "description_fr": "L'Iḍāfa (état construit) exprime la possession sans préposition. Le premier nom perd le Tanwin.",
        "grammar": "N1 + N2(défini/génitif) = N1 de N2\nكِتَابُ الطَّالِبِ (le livre de l'étudiant) — Tanwin de كِتَابٌ disparaît\nبَيْتُ اللَّهِ (la Maison de Dieu = la Ka'ba)",
        "vocab": [("بَيْتُ اللَّهِ", "la Maison de Dieu", "bayt ullāh"), ("كِتَابُ الطَّالِبِ", "le livre de l'étudiant", "kitāb uṭ-ṭālib"), ("مَسْجِدُ النَّبِيِّ", "la mosquée du Prophète", "masjid an-nabī")],
    },
    {
        "number": 22, "title_ar": "الدَّرْسُ الثَّانِي وَالْعِشْرُونَ", "title_fr": "Leçon 22 — Les cas grammaticaux (I'rāb)",
        "description_fr": "Les 3 cas arabes : Raf' (nominatif), Naṣb (accusatif), Jarr (génitif). Marqueurs de cas.",
        "grammar": "ـُ / ـٌ → Raf' (sujet) : جَاءَ الطَّالِبُ (l'étudiant est venu)\nـَ / ـً → Naṣb (objet direct, etc.) : رَأَيْتُ الطَّالِبَ\nـِ / ـٍ → Jarr (après préposition) : ذَهَبْتُ إِلَى الطَّالِبِ",
        "vocab": [("رَفْعٌ", "nominatif", "raf'"), ("نَصْبٌ", "accusatif", "naṣb"), ("جَرٌّ", "génitif", "jarr"), ("إِعْرَابٌ", "déclinaison", "i'rāb"), ("مَرْفُوعٌ", "au nominatif", "marfū'"), ("مَنْصُوبٌ", "à l'accusatif", "manṣūb"), ("مَجْرُورٌ", "au génitif", "majrūr")],
    },
    {
        "number": 23, "title_ar": "الدَّرْسُ الثَّالِث وَالْعِشْرُونَ", "title_fr": "Leçon 23 — Révision et évaluation finale",
        "description_fr": "Révision complète du Tome 1. Dialogue libre en arabe. Préparation au Tome 2.",
        "grammar": "Révision des points clés :\n1. La phrase nominale (sujet + prédicat sans verbe)\n2. La phrase verbale (verbe + sujet)\n3. L'Iḍāfa (état construit)\n4. La négation (لَيْسَ / لَا / لَمْ / لَنْ)\n5. Les cas grammaticaux",
        "vocab": [("مُرَاجَعَةٌ", "révision", "murāja'ah"), ("اخْتِبَارٌ", "examen / test", "ikhtibār"), ("نَجَاحٌ", "succès", "najāḥ"), ("تَقَدُّمٌ", "progrès", "taqaddum")],
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# Program 4 — Tajwid Théorique (12 modules)
# ══════════════════════════════════════════════════════════════════════════════

TAJWID_MODULES = [
    {
        "number": 1, "title_ar": "تَعْرِيفُ التَّجْوِيد", "title_fr": "Module 1 — Définition et importance du Tajwid",
        "description_fr": "Le Tajwid (تَجْوِيد) signifie 'amélioration, embellissement'. Science qui enseigne à réciter le Coran comme le Prophète ﷺ l'a récité.",
        "items": [
            {"title_ar": "تَعْرِيفُ التَّجْوِيد", "content_fr": "Linguistiquement : améliorer, embellir. Techniquement : donner à chaque lettre son droit (ḥaqq) et son dû (mustaḥaqq) en termes de points d'articulation et caractéristiques.", "type": "RULE"},
            {"title_ar": "حُكْمُ تَعَلُّمِ التَّجْوِيد", "content_fr": "Apprendre le Tajwid est une obligation collective (Farḍ Kifāya). Le réciter correctement est une obligation individuelle (Farḍ 'Ayn) pour tout musulman récitant le Coran.", "type": "RULE"},
            {"title_ar": "اللَّحْن", "content_fr": "L'erreur de récitation (Laḥn) : جَلِيٌّ (flagrante — change le sens) ou خَفِيٌّ (subtile — affecte les règles du Tajwid).", "type": "RULE"},
        ],
    },
    {
        "number": 2, "title_ar": "مَخَارِجُ الْحُرُوف", "title_fr": "Module 2 — Points d'articulation (Makhārij)",
        "description_fr": "Les 17 points d'articulation répartis en 5 zones. Chaque lettre sort d'un point précis dans l'appareil phonatoire.",
        "items": [
            {"title_ar": "الجَوْفُ (الفَرَاغ)", "content_fr": "Zone 1 — Cavité : les lettres de prolongation ا و ي. Le son émerge de la cavité buccale.", "type": "RULE", "metadata": {"zone": 1, "letters": ["ا", "و", "ي"]}},
            {"title_ar": "الحَلْق (3 points)", "content_fr": "Zone 2 — Gorge :\n• Fond de gorge : أ ه\n• Milieu de gorge : ع ح\n• Haut de gorge : غ خ", "type": "RULE", "metadata": {"zone": 2, "letters": ["أ","ه","ع","ح","غ","خ"]}},
            {"title_ar": "اللِّسَان (10 points)", "content_fr": "Zone 3 — Langue : 18 lettres produites par différentes parties de la langue (racine, dos, bout, côtés).", "type": "RULE", "metadata": {"zone": 3}},
            {"title_ar": "الشَّفَتَان", "content_fr": "Zone 4 — Lèvres :\n• ف : lèvre inférieure + dents supérieures\n• و : lèvres légèrement ouvertes\n• ب م : lèvres closes", "type": "RULE", "metadata": {"zone": 4, "letters": ["ف","و","ب","م"]}},
            {"title_ar": "الخَيْشُوم", "content_fr": "Zone 5 — Fosses nasales : siège du Ghunna (غُنَّة), la nasalisation qui accompagne ن et م.", "type": "RULE", "metadata": {"zone": 5, "letters": ["ن","م"]}},
        ],
    },
    {
        "number": 3, "title_ar": "صِفَاتُ الْحُرُوف", "title_fr": "Module 3 — Caractéristiques des lettres (Sifāt)",
        "description_fr": "Chaque lettre possède des attributs fixes (Lāzima) qui lui confèrent son son unique.",
        "items": [
            {"title_ar": "الجَهْر / الهَمْس", "content_fr": "SONORITÉ :\nجَهْر (sonore) — corde vocale vibre : ب ج د ذ ر ز ض ط ظ ع غ ق ل م ن و ي\nهَمْس (sourd) — corde vocale ne vibre pas : ت ث ح خ س ش ص ف ك ه", "type": "RULE"},
            {"title_ar": "الشِّدَّة / الرَّخَاوَة / التَّوَسُّط", "content_fr": "MODE ARTICULATOIRE :\nشِدَّة (occlusif) : ء ب ت ج د ط ك ق — son bloqué\nرَخَاوَة (fricatif) : ث ح خ ذ ز س ش ص ض ظ غ ف ه و ي — son continu\nتَوَسُّط (intermédiaire) : ل م ن ر ع", "type": "RULE"},
            {"title_ar": "الاسْتِعْلَاء / الاسْتِفَال", "content_fr": "HAUTEUR (langue) :\nاسْتِعْلَاء (élevé) — 7 lettres emphatiques : خ ص ض ط ظ غ ق → son grave, langue monte\nاسْتِفَال (bas) — les autres lettres → son aigu, langue reste basse", "type": "RULE", "metadata": {"isti'la_letters": ["خ","ص","ض","ط","ظ","غ","ق"]}},
            {"title_ar": "الإِطْبَاق / الانْفِتَاح", "content_fr": "FERMETURE DU PALAIS :\nإِطْبَاق (fermé) — 4 lettres emphatiques : ص ض ط ظ → palais et langue se rapprochent\nانْفِتَاح (ouvert) — toutes les autres lettres", "type": "RULE"},
        ],
    },
    {
        "number": 4, "title_ar": "النُّون السَّاكِنَة وَالتَّنْوِين", "title_fr": "Module 4 — Nūn Sākina et Tanwin (4 règles)",
        "description_fr": "Règle centrale du Tajwid. Quand un Nūn sans voyelle (ou Tanwin) est suivi d'une lettre, une des 4 règles s'applique.",
        "items": [
            {"title_ar": "الإِظْهَار الْحَلْقِي", "content_fr": "IẒHĀR — Clarté\nDevant les 6 lettres gutturales : ء ه ع ح غ خ\nLe Nūn se prononce clairement, sans nasalisation.\nEx : مَنْ آمَنَ — أَنْعَمْتَ", "type": "RULE", "metadata": {"letters": ["ء","ه","ع","ح","غ","خ"]}},
            {"title_ar": "الإِدْغَام بِغُنَّة / بِغَيْرِ غُنَّة", "content_fr": "IDGHĀM — Fusion\n• Avec Ghunna (ي ن م و) : le Nūn se fond avec nasalisation\n• Sans Ghunna (ل ر) : le Nūn se fond sans nasalisation\nEx avec Ghunna : مَنْ يَعْمَلُ\nEx sans Ghunna : مِنْ رَبِّهِمْ", "type": "RULE", "metadata": {"with_ghunna": ["ي","ن","م","و"], "without_ghunna": ["ل","ر"]}},
            {"title_ar": "الإِقْلَاب", "content_fr": "IQLĀB — Transformation\nDevant ب uniquement : le Nūn se transforme en Mīm avec Ghunna.\nEx : أَنْبِئُونِي → se lit comme أَمْبِئُونِي", "type": "RULE", "metadata": {"letters": ["ب"]}},
            {"title_ar": "الإِخْفَاء الْحَقِيقِي", "content_fr": "IKHFĀ' — Dissimulation\nDevant les 15 lettres restantes : son entre le Nūn clair et la fusion.\nLes 15 lettres : ت ث ج د ذ ز س ش ص ض ط ظ ف ق ك\nEx : مَنْ كَانَ — إِنْ كُنْتُمْ", "type": "RULE", "metadata": {"letters": ["ت","ث","ج","د","ذ","ز","س","ش","ص","ض","ط","ظ","ف","ق","ك"]}},
        ],
    },
    {
        "number": 5, "title_ar": "الْمِيمُ السَّاكِنَة", "title_fr": "Module 5 — Mīm Sākina (3 règles)",
        "description_fr": "Règles du Mīm sans voyelle. Simpler que celles du Nūn mais tout aussi importantes.",
        "items": [
            {"title_ar": "الإِخْفَاء الشَّفَوِي", "content_fr": "Devant ب uniquement : le Mīm est dissimulé avec Ghunna (nasalisation).\nEx : هُمْ بِهِ → les lèvres ne se ferment pas complètement.", "type": "RULE"},
            {"title_ar": "الإِدْغَام الشَّفَوِي", "content_fr": "Devant م uniquement : le Mīm se fusionne avec le Mīm suivant avec Ghunna.\nEx : لَكُمْ مَا تَشَاؤُونَ", "type": "RULE"},
            {"title_ar": "الإِظْهَار الشَّفَوِي", "content_fr": "Devant toutes les 26 autres lettres : le Mīm se prononce clairement.\nEx : عَلَيْهِمْ غَيْرِ — les lèvres se ferment nettement sur le Mīm.", "type": "RULE"},
        ],
    },
    {
        "number": 6, "title_ar": "الغُنَّة", "title_fr": "Module 6 — La Ghunna (nasalisation)",
        "description_fr": "La Ghunna est la résonance nasale produite dans les fosses nasales. Elle caractérise principalement Nūn et Mīm.",
        "items": [
            {"title_ar": "تَعْرِيفُ الغُنَّة", "content_fr": "La Ghunna est un son nasal émis depuis la fosse nasale, indépendant de l'articulation. Elle accompagne toujours ن et م avec Shadda.", "type": "RULE"},
            {"title_ar": "دَرَجَاتُ الغُنَّة", "content_fr": "Niveaux de Ghunna :\n1. Complète (2 temps) : ن م Mushaddad\n2. Idghām avec Ghunna\n3. Ikhfā'\n4. Partielle : Nūn/Mīm Sākina dans Iẓhār", "type": "RULE"},
            {"title_ar": "مِثَال : إِنَّ", "content_fr": "إِنَّ : Nūn avec Shadda → Ghunna obligatoire de 2 temps.", "type": "EXAMPLE"},
        ],
    },
    {
        "number": 7, "title_ar": "الْمُدُودُ", "title_fr": "Module 7 — Les types de Madd",
        "description_fr": "Le Madd (prolongation) est fondamental. Il existe 2 catégories : le Madd Aṣlī (naturel) et les Madds Far'ī (secondaires).",
        "items": [
            {"title_ar": "مَدٌّ طَبِيعِي / أَصْلِي", "content_fr": "MADD ṬABĪ'Ī — 2 temps\nTout Madd sans cause (Hamza ou Sukun après). Les 3 lettres de prolongation : ا و ي\nEx : قَالَ / قِيلَ / يَقُولُ", "type": "RULE"},
            {"title_ar": "مَدٌّ وَاجِبٌ مُتَّصِل", "content_fr": "MADD MUTTAṢIL — 4 ou 5 temps\nLettre de Madd + Hamza dans le MÊME mot.\nEx : جَاءَ / سُوءٍ / الَّذِي جَاءَكُم", "type": "RULE"},
            {"title_ar": "مَدٌّ جَائِزٌ مُنْفَصِل", "content_fr": "MADD MUNFAṢIL — 2 à 5 temps selon la qirā'a\nLettre de Madd en fin de mot + Hamza au DÉBUT du mot suivant.\nEx : قُوا أَنْفُسَكُمْ / إِنَّا أَعْطَيْنَاكَ", "type": "RULE"},
            {"title_ar": "مَدٌّ لَازِمٌ", "content_fr": "MADD LĀZIM — 6 temps obligatoires\nLettre de Madd + Sukun ou Shadda permanent dans le même mot.\nEx : الضَّالِّين / حَاجَّ / آلآنَ", "type": "RULE"},
            {"title_ar": "مَدُّ الْعِوَض", "content_fr": "MADD 'IWAḌ — 2 temps\nTanwin Fath sur Alif en fin de mot lors du Waqf.\nEx : عَلِيمًا (pause) → يُقرأ عَلِيمَا", "type": "RULE"},
            {"title_ar": "مَدُّ الصِّلَة", "content_fr": "MADD ṢILAH — prolongation du pronom هُ/هِ\nQuand le pronom est entre deux voyelles, il se prolonge.\nEx : إِنَّهُۥ كَانَ (le هُ se prolonge de 2 temps)", "type": "RULE"},
        ],
    },
    {
        "number": 8, "title_ar": "التَّفْخِيم وَالتَّرْقِيق", "title_fr": "Module 8 — Emphatique (Tafkhīm) et léger (Tarqīq)",
        "description_fr": "Deux qualités de résonance qui modifient le timbre des lettres. Essentielles pour les lettres emphatiques.",
        "items": [
            {"title_ar": "التَّفْخِيم", "content_fr": "TAFKHĪM — Emphatique (grave)\n7 lettres toujours emphatiques : خ ص ض ط ظ غ ق\nLe Rā (ر) est emphatique dans certains contextes.\nSon grave, cavité buccale pleine.", "type": "RULE"},
            {"title_ar": "التَّرْقِيق", "content_fr": "TARQĪQ — Léger (aigu)\nToutes les autres lettres. Le Rā est léger devant Kasra ou Yā de Madd.\nSon léger, cavité buccale vide.", "type": "RULE"},
            {"title_ar": "الرَّاء بَيْنَهُمَا", "content_fr": "LE RĀ — entre emphatique et léger\nEmphatique : رَبَّنَا / رُسُل / مِصْر (pause)\nLéger : رِزْق / كَرِيم / شَعِير", "type": "RULE"},
            {"title_ar": "لَفْظُ الجَلَالَة", "content_fr": "LE NOM ALLAH — cas particulier\nاللَّه après Fatha ou Damma → emphatique : قَالَ اللَّهُ\nاللَّه après Kasra → léger : بِسْمِ اللَّهِ", "type": "RULE"},
        ],
    },
    {
        "number": 9, "title_ar": "اللَّامَات", "title_fr": "Module 9 — Les Lāms (article, verbe être, nom d'Allah)",
        "description_fr": "Les Lāms du Coran ont des règles spécifiques selon leur position et le contexte.",
        "items": [
            {"title_ar": "لَام الشَّمْسِيَّة", "content_fr": "14 lettres solaires → le Lām de l'article disparaît (assimilation).\nEx : الشَّمْس → ash-shams / الرَّحِيم → ar-raḥīm", "type": "RULE", "metadata": {"letters": ["ت","ث","د","ذ","ر","ز","س","ش","ص","ض","ط","ظ","ل","ن"]}},
            {"title_ar": "لَام الْقَمَرِيَّة", "content_fr": "14 lettres lunaires → le Lām se prononce clairement.\nEx : الْقَمَر → al-qamar / الْكِتَاب → al-kitāb", "type": "RULE"},
            {"title_ar": "لَفْظُ الجَلَالَة", "content_fr": "لَام لَفْظِ الجَلَالَة (le Lām dans Allah) : toujours léger (Tarqīq) sauf après Fatha/Damma.", "type": "RULE"},
        ],
    },
    {
        "number": 10, "title_ar": "الْوَقْف وَالابْتِدَاء", "title_fr": "Module 10 — Règles de pause (Waqf) et reprise (Ibtidā')",
        "description_fr": "La pause (Waqf) est l'arrêt de la voix à la fin d'un mot. Ses règles affectent la prononciation de la lettre finale.",
        "items": [
            {"title_ar": "أَنْوَاعُ الْوَقْف", "content_fr": "Types de Waqf :\n• Waqf Tāmm (complet) م : sens complet\n• Waqf Kāfī : acceptable grammaticalement\n• Waqf Ḥasan : sens partiel mais utilisable\n• Waqf Qabīḥ : ne doit pas être utilisé — tronque le sens", "type": "RULE"},
            {"title_ar": "أَحْكَامُ الْوَقْف", "content_fr": "En fin de mot lors de la pause :\n• Tanwin → son court (ou Alif si Tanwin Fath)\n• Tā Marbūṭa → devient H aspiré\n• Sukun apparent sur la dernière lettre", "type": "RULE"},
            {"title_ar": "الابْتِدَاء", "content_fr": "Reprise après la pause :\n• Reprendre depuis un mot où le sens est intact\n• Si reprise après Hamzat Waṣl, elle se prononce\n• Ne jamais reprendre au milieu d'une règle de Tajwid active", "type": "RULE"},
        ],
    },
    {
        "number": 11, "title_ar": "هَمْزَةُ الْوَصْل وَالْقَطْع", "title_fr": "Module 11 — Hamzat Waṣl et Hamzat Qaṭ'",
        "description_fr": "Deux types de Hamza initiale avec des comportements différents en liaison.",
        "items": [
            {"title_ar": "هَمْزَةُ الْوَصْل", "content_fr": "HAMZAT WAṢL — Hamza de jonction\nÉcrite sur Alif sans Hamza (ا) ou avec signe ـٱ.\nElle disparaît en liaison : سَمِعَ الرَّسُولُ → sama'ar-rasūl\nPrésente dans : l'article ال, les verbes de forme VII-X, certains noms", "type": "RULE"},
            {"title_ar": "هَمْزَةُ الْقَطْع", "content_fr": "HAMZAT QAṬ' — Hamza ferme\nÉcrite avec signe Hamza (أ إ ؤ ئ ء).\nElle se prononce TOUJOURS, même en liaison.\nEx : أَكَلَ — إِنَّ — يُؤْمِن", "type": "RULE"},
            {"title_ar": "فَرْق بَيْنَهُمَا", "content_fr": "Mnémotechnique : Hamzat Waṣl disparaît comme une passerelle (waṣl = liaison). Hamzat Qaṭ' résiste comme une coupure (qaṭ' = coupure).", "type": "RULE"},
        ],
    },
    {
        "number": 12, "title_ar": "مُرَاجَعَة وَتَطْبِيق", "title_fr": "Module 12 — Révision globale et application pratique",
        "description_fr": "Application de toutes les règles sur des passages coraniques réels. Évaluation de la maîtrise du Tajwid.",
        "items": [
            {"title_ar": "تَطْبِيق عَلَى سُورَةِ الْفَاتِحَة", "content_fr": "Analyse complète de la Fātiḥa :\n• Madd Muttaṣil : الرَّحِيم\n• Lām Shamsiyya : الرَّحْمَٰن / الرَّحِيم / الدِّين\n• Idghām : صِرَاطَ الَّذِين (ط non concerné ici)\n• Tafkhīm du Rā : الرَّحْمَٰن, صِرَاطَ, الْمَغْضُوب", "content_ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ ﴿١﴾ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ﴿٢﴾", "type": "EXAMPLE"},
            {"title_ar": "تَطْبِيق عَلَى سُورَةِ الْإِخْلَاص", "content_fr": "Analyse de Al-Ikhlāṣ :\n• قُلْ هُوَ : Madd naturel dans هُوَ\n• اللَّهُ أَحَدٌ : Tafkhīm du Lām dans Allah\n• لَمْ يَلِدْ : Mīm Sākina devant ي → Iẓhār Shafawī\n• كُفُوًا أَحَدٌ : Tanwin Fath + Hamza = pause possible ici", "content_ar": "قُلْ هُوَ اللَّهُ أَحَدٌ ﴿١﴾ اللَّهُ الصَّمَدُ ﴿٢﴾ لَمْ يَلِدْ وَلَمْ يُولَدْ ﴿٣﴾ وَلَمْ يَكُن لَّهُۥ كُفُوًا أَحَدٌ ﴿٤﴾", "type": "EXAMPLE"},
        ],
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# Seeding functions
# ══════════════════════════════════════════════════════════════════════════════

def _seed_alphabet(db, program: CurriculumProgram):
    for letter in ARABIC_LETTERS:
        num, name_fr, isolated, initial, medial, final, translit, desc = letter
        audio_file = LETTER_AUDIO.get(name_fr)
        audio_url = f"/static/audio/letters/{audio_file}.mp3" if audio_file else None
        unit = CurriculumUnit(
            curriculum_program_id=program.id,
            unit_type=UnitType.LETTER,
            number=num,
            title_ar=isolated,
            title_fr=f"Lettre {num} — {name_fr}",
            description_fr=desc,
            audio_url=audio_url,
            sort_order=num,
            total_items=4,
        )
        db.add(unit)
        db.flush()

        glyphs = [isolated, initial, medial, final]
        for pos_idx, (pos_key, pos_fr, pos_desc) in enumerate(POSITIONS):
            glyph = glyphs[pos_idx]
            item = CurriculumItem(
                curriculum_unit_id=unit.id,
                item_type=ItemType.LETTER_FORM,
                number=pos_idx + 1,
                title_ar=glyph,
                title_fr=f"{name_fr} — {pos_fr}",
                content_fr=pos_desc,
                transliteration=translit,
                letter_position=pos_key,
                audio_url=audio_url,
                sort_order=pos_idx,
            )
            db.add(item)
    program.total_units = len(ARABIC_LETTERS)


def _seed_voyelles_syllabes(db, program: CurriculumProgram):
    """Seed Voyelles et Syllabes program using Nourania chapters 2-5."""
    chapters = [ch for ch in NOURANIA_CHAPTERS if ch["number"] in (2, 3, 4, 5)]
    for idx, chapter in enumerate(chapters):
        unit = CurriculumUnit(
            curriculum_program_id=program.id,
            unit_type=UnitType.MODULE,
            number=idx + 1,
            title_ar=chapter["title_ar"],
            title_fr=chapter["title_fr"],
            description_fr=chapter["description_fr"],
            sort_order=idx + 1,
            total_items=len(chapter["items"]),
        )
        db.add(unit)
        db.flush()

        for i, it in enumerate(chapter["items"]):
            item = CurriculumItem(
                curriculum_unit_id=unit.id,
                item_type=ItemType[it.get("type", "COMBINATION")],
                number=i + 1,
                title_ar=it["title_ar"],
                title_fr=it.get("title_fr"),
                content_fr=it.get("content_fr"),
                transliteration=it.get("transliteration"),
                extra_data=it.get("metadata"),
                sort_order=i,
            )
            db.add(item)
    program.total_units = len(chapters)


def _seed_nourania(db, program: CurriculumProgram):
    for chapter in NOURANIA_CHAPTERS:
        unit = CurriculumUnit(
            curriculum_program_id=program.id,
            unit_type=UnitType.CHAPTER,
            number=chapter["number"],
            title_ar=chapter["title_ar"],
            title_fr=chapter["title_fr"],
            description_fr=chapter["description_fr"],
            sort_order=chapter["number"],
            total_items=len(chapter["items"]),
        )
        db.add(unit)
        db.flush()

        for i, it in enumerate(chapter["items"]):
            item = CurriculumItem(
                curriculum_unit_id=unit.id,
                item_type=ItemType[it.get("type", "COMBINATION")],
                number=i + 1,
                title_ar=it["title_ar"],
                title_fr=it.get("title_fr"),
                content_fr=it.get("content_fr"),
                transliteration=it.get("transliteration"),
                extra_data=it.get("metadata"),
                sort_order=i,
            )
            db.add(item)
    program.total_units = len(NOURANIA_CHAPTERS)


def _seed_medine_t1(db, program: CurriculumProgram):
    for lesson in MEDINE_T1_LESSONS:
        # Guard: skip if a unit with this number already exists (idempotent)
        existing_unit = db.query(CurriculumUnit).filter_by(
            curriculum_program_id=program.id,
            number=lesson["number"],
        ).first()
        if existing_unit:
            continue

        unit = CurriculumUnit(
            curriculum_program_id=program.id,
            unit_type=UnitType.LESSON,
            number=lesson["number"],
            title_ar=lesson["title_ar"],
            title_fr=lesson["title_fr"],
            description_fr=lesson["description_fr"],
            sort_order=lesson["number"],
            total_items=1 + len(lesson["vocab"]),  # 1 grammar + vocab items
        )
        db.add(unit)
        db.flush()

        # Grammar item
        grammar_item = CurriculumItem(
            curriculum_unit_id=unit.id,
            item_type=ItemType.GRAMMAR_POINT,
            number=1,
            title_ar="قَاعِدَة",
            title_fr="Règle de grammaire",
            content_fr=lesson["grammar"],
            sort_order=0,
        )
        db.add(grammar_item)

        # Vocabulary items
        for j, (ar, fr, translit) in enumerate(lesson["vocab"]):
            vocab_item = CurriculumItem(
                curriculum_unit_id=unit.id,
                item_type=ItemType.VOCABULARY,
                number=j + 2,
                title_ar=ar,
                title_fr=fr,
                transliteration=translit,
                sort_order=j + 1,
            )
            db.add(vocab_item)

    program.total_units = len(MEDINE_T1_LESSONS)


def _seed_tajwid(db, program: CurriculumProgram):
    for module in TAJWID_MODULES:
        unit = CurriculumUnit(
            curriculum_program_id=program.id,
            unit_type=UnitType.MODULE,
            number=module["number"],
            title_ar=module["title_ar"],
            title_fr=module["title_fr"],
            description_fr=module["description_fr"],
            sort_order=module["number"],
            total_items=len(module["items"]),
        )
        db.add(unit)
        db.flush()

        for i, it in enumerate(module["items"]):
            item = CurriculumItem(
                curriculum_unit_id=unit.id,
                item_type=ItemType[it.get("type", "RULE")],
                number=i + 1,
                title_ar=it["title_ar"],
                content_fr=it.get("content_fr"),
                content_ar=it.get("content_ar"),
                extra_data=it.get("metadata"),
                sort_order=i,
            )
            db.add(item)
    program.total_units = len(TAJWID_MODULES)


def _seed_hifz(db, program: CurriculumProgram):
    """Create 30 Juz units, each with surah items (soft reference to surahs table)."""
    # Simplified Juz mapping (surah ranges per Juz)
    JUZ_SURAH_RANGES = [
        (1, [(1, 1, 7), (2, 1, 141)]),          # Juz 1: Al-Fatiha + début Baqara
        (2, [(2, 142, 252)]),                    # Juz 2
        (3, [(2, 253, 286), (3, 1, 92)]),        # Juz 3
        (4, [(3, 93, 200), (4, 1, 23)]),         # Juz 4
        (5, [(4, 24, 147)]),                     # Juz 5
        (6, [(4, 148, 176), (5, 1, 81)]),        # Juz 6
        (7, [(5, 82, 120), (6, 1, 110)]),        # Juz 7
        (8, [(6, 111, 165), (7, 1, 87)]),        # Juz 8
        (9, [(7, 88, 206), (8, 1, 40)]),         # Juz 9
        (10, [(8, 41, 75), (9, 1, 92)]),         # Juz 10
        (11, [(9, 93, 129), (10, 1, 109), (11, 1, 5)]),   # Juz 11
        (12, [(11, 6, 123), (12, 1, 52)]),       # Juz 12
        (13, [(12, 53, 111), (13, 1, 43), (14, 1, 52)]),  # Juz 13
        (14, [(15, 1, 99), (16, 1, 128)]),       # Juz 14
        (15, [(17, 1, 111), (18, 1, 74)]),       # Juz 15
        (16, [(18, 75, 110), (19, 1, 98), (20, 1, 135)]), # Juz 16
        (17, [(21, 1, 112), (22, 1, 78)]),       # Juz 17
        (18, [(23, 1, 118), (24, 1, 64)]),       # Juz 18
        (19, [(25, 1, 77), (26, 1, 227), (27, 1, 1)]),   # Juz 19
        (20, [(27, 2, 93), (28, 1, 88)]),        # Juz 20
        (21, [(29, 1, 69), (30, 1, 60), (31, 1, 34)]),   # Juz 21
        (22, [(32, 1, 30), (33, 1, 73), (34, 1, 54)]),   # Juz 22
        (23, [(35, 1, 45), (36, 1, 83), (37, 1, 144)]),  # Juz 23
        (24, [(37, 145, 182), (38, 1, 88), (39, 1, 75)]),# Juz 24
        (25, [(40, 1, 85), (41, 1, 46)]),        # Juz 25
        (26, [(42, 1, 53), (43, 1, 89), (44, 1, 59), (45, 1, 37), (46, 1, 1)]), # Juz 26
        (27, [(46, 2, 35), (47, 1, 38), (48, 1, 29), (49, 1, 18), (50, 1, 45), (51, 1, 30)]), # Juz 27
        (28, [(51, 31, 60), (52, 1, 49), (53, 1, 62), (54, 1, 55), (55, 1, 78), (56, 1, 96), (57, 1, 29)]), # Juz 28
        (29, [(58, 1, 22), (59, 1, 24), (60, 1, 13), (61, 1, 14), (62, 1, 11), (63, 1, 11), (64, 1, 18), (65, 1, 12), (66, 1, 12), (67, 1, 30), (68, 1, 52), (69, 1, 52), (70, 1, 44), (71, 1, 28), (72, 1, 28), (73, 1, 20), (74, 1, 56), (75, 1, 40), (76, 1, 31), (77, 1, 50)]), # Juz 29
        (30, [(78, 1, 40), (79, 1, 46), (80, 1, 42), (81, 1, 29), (82, 1, 19), (83, 1, 36), (84, 1, 25), (85, 1, 22), (86, 1, 17), (87, 1, 19), (88, 1, 26), (89, 1, 30), (90, 1, 20), (91, 1, 15), (92, 1, 21), (93, 1, 11), (94, 1, 8), (95, 1, 8), (96, 1, 19), (97, 1, 5), (98, 1, 8), (99, 1, 8), (100, 1, 11), (101, 1, 11), (102, 1, 8), (103, 1, 3), (104, 1, 9), (105, 1, 5), (106, 1, 4), (107, 1, 7), (108, 1, 3), (109, 1, 6), (110, 1, 3), (111, 1, 5), (112, 1, 4), (113, 1, 5), (114, 1, 6)]), # Juz 30
    ]

    for juz_num, surah_ranges in JUZ_SURAH_RANGES:
        unit = CurriculumUnit(
            curriculum_program_id=program.id,
            unit_type=UnitType.JUZ,
            number=juz_num,
            title_ar=f"الجزء {juz_num}",
            title_fr=f"Juz {juz_num}",
            description_fr=f"Le {juz_num}ème juz du Coran.",
            sort_order=juz_num,
            total_items=len(surah_ranges),
        )
        db.add(unit)
        db.flush()

        for i, (surah_num, verse_start, verse_end) in enumerate(surah_ranges):
            item = CurriculumItem(
                curriculum_unit_id=unit.id,
                item_type=ItemType.SURAH_SEGMENT,
                number=i + 1,
                title_ar=f"سورة {surah_num}",
                title_fr=f"Sourate {surah_num} — versets {verse_start}-{verse_end}",
                surah_number=surah_num,
                verse_start=verse_start,
                verse_end=verse_end,
                sort_order=i,
            )
            db.add(item)

    program.total_units = 30


PROGRAMS_META = [
    # ── Apprendre à lire ──────────────────────────────────────────────────
    {
        "curriculum_type": CurriculumType.ALPHABET_ARABE,
        "category": ProgramCategory.APPRENDRE_A_LIRE,
        "title_ar": "الأبجدية العربية",
        "title_fr": "Alphabet Arabe",
        "description_fr": "Parcours progressif pour maîtriser les 28 lettres arabes dans leurs 4 positions : isolée, initiale, médiane et finale. Fondation indispensable pour tout apprenant.",
        "sort_order": 1,
        "seeder": _seed_alphabet,
    },
    {
        "curriculum_type": CurriculumType.VOYELLES_SYLLABES,
        "category": ProgramCategory.APPRENDRE_A_LIRE,
        "title_ar": "الحركات والمقاطع",
        "title_fr": "Voyelles et Syllabes",
        "description_fr": "Apprenez à combiner les lettres avec les voyelles courtes (Fatha, Kasra, Damma), la nunation (Tanwin), le Sukun et les prolongations (Madd). L'étape clé pour passer des lettres à la lecture.",
        "sort_order": 2,
        "seeder": _seed_voyelles_syllabes,
    },
    {
        "curriculum_type": CurriculumType.QAIDA_NOURANIA,
        "category": ProgramCategory.APPRENDRE_A_LIRE,
        "title_ar": "القاعدة النورانية",
        "title_fr": "Lecture niveau 2",
        "description_fr": "Les 17 chapitres de la Qa'ida Nourania : lettres, voyelles, tanwin, sukun, madd, shadda, et toutes les règles de lecture avancées.",
        "sort_order": 3,
        "seeder": _seed_nourania,
    },
    # ── Comprendre l'arabe ────────────────────────────────────────────────
    {
        "curriculum_type": CurriculumType.MEDINE_T1,
        "category": ProgramCategory.COMPRENDRE_ARABE,
        "title_ar": "سلسلة المدينة — الجزء الأول",
        "title_fr": "Médine Tome 1",
        "description_fr": "Les 23 leçons du Tome 1 de Médine : grammaire arabe fondamentale (phrase nominale, pronoms, verbes, cas) avec vocabulaire thématique en Arabe/Français.",
        "sort_order": 4,
        "seeder": _seed_medine_t1,
    },
    # ── Lire et Apprendre le Coran ────────────────────────────────────────
    {
        "curriculum_type": CurriculumType.TAJWID,
        "category": ProgramCategory.CORAN,
        "title_ar": "التجويد النظري",
        "title_fr": "Tajwid Théorique",
        "description_fr": "12 modules sur les règles fondamentales du Tajwid : makhārij, sifāt, nūn sākina, mīm sākina, les madds, tafkhīm/tarqīq, waqf et ibtidā'.",
        "sort_order": 5,
        "seeder": _seed_tajwid,
    },
    {
        "curriculum_type": CurriculumType.HIFZ_REVISION,
        "category": ProgramCategory.CORAN,
        "title_ar": "الحفظ والمراجعة",
        "title_fr": "Hifz & Révision Coran",
        "description_fr": "Suivi précis de la mémorisation et révision du Coran. Les 30 Juz avec leurs sourates et versets. Tracking au verset près.",
        "sort_order": 6,
        "seeder": _seed_hifz,
    },
]


def _update_alphabet_audio(db) -> None:
    """Backfill audio_url on existing alphabet units & items."""
    program = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.ALPHABET_ARABE
    ).first()
    if not program:
        return

    units = db.query(CurriculumUnit).filter_by(
        curriculum_program_id=program.id
    ).all()

    updated = 0
    for unit in units:
        # Extract letter name from title_fr: "Lettre 1 — Alif" → "Alif"
        parts = (unit.title_fr or "").split(" — ", 1)
        if len(parts) < 2:
            continue
        name_fr = parts[1]
        audio_file = LETTER_AUDIO.get(name_fr)
        if not audio_file:
            continue

        audio_url = f"/static/audio/letters/{audio_file}.mp3"
        if unit.audio_url != audio_url:
            unit.audio_url = audio_url
            updated += 1

        items = db.query(CurriculumItem).filter_by(
            curriculum_unit_id=unit.id
        ).all()
        for item in items:
            if item.audio_url != audio_url:
                item.audio_url = audio_url

    if updated:
        db.commit()
        print(f"  ✓ Updated audio_url on {updated} alphabet units.")
    else:
        print("  Alphabet audio_url already up to date.")


def _update_existing_programs(db) -> None:
    """Update existing programs: rename Nourania → Lecture niveau 2, set categories, add Voyelles et Syllabes."""
    # Update Nourania title
    nourania = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.QAIDA_NOURANIA
    ).first()
    if nourania and nourania.title_fr != "Lecture niveau 2":
        nourania.title_fr = "Lecture niveau 2"
        nourania.category = ProgramCategory.APPRENDRE_A_LIRE
        print("  ✓ Renamed Qa'ida Nourania → Lecture niveau 2")

    # Set categories on existing programs
    category_map = {
        CurriculumType.ALPHABET_ARABE: ProgramCategory.APPRENDRE_A_LIRE,
        CurriculumType.QAIDA_NOURANIA: ProgramCategory.APPRENDRE_A_LIRE,
        CurriculumType.MEDINE_T1: ProgramCategory.COMPRENDRE_ARABE,
        CurriculumType.TAJWID: ProgramCategory.CORAN,
        CurriculumType.HIFZ_REVISION: ProgramCategory.CORAN,
    }
    for ctype, cat in category_map.items():
        prog = db.query(CurriculumProgram).filter_by(curriculum_type=ctype).first()
        if prog and prog.category != cat:
            prog.category = cat

    # Add Voyelles et Syllabes if not exists
    vs = db.query(CurriculumProgram).filter_by(
        curriculum_type=CurriculumType.VOYELLES_SYLLABES
    ).first()
    if not vs:
        vs_meta = next(m for m in PROGRAMS_META if m["curriculum_type"] == CurriculumType.VOYELLES_SYLLABES)
        seeder = vs_meta["seeder"]
        meta_copy = {k: v for k, v in vs_meta.items() if k != "seeder"}
        vs = CurriculumProgram(**meta_copy)
        db.add(vs)
        db.flush()
        seeder(db, vs)
        db.flush()
        print(f"  ✓ Added Voyelles et Syllabes ({vs.total_units} units)")

    # Update sort_order
    order_map = {
        CurriculumType.ALPHABET_ARABE: 1,
        CurriculumType.VOYELLES_SYLLABES: 2,
        CurriculumType.QAIDA_NOURANIA: 3,
        CurriculumType.MEDINE_T1: 4,
        CurriculumType.TAJWID: 5,
        CurriculumType.HIFZ_REVISION: 6,
    }
    for ctype, order in order_map.items():
        prog = db.query(CurriculumProgram).filter_by(curriculum_type=ctype).first()
        if prog:
            prog.sort_order = order

    db.commit()


def seed_curriculum(db=None) -> None:
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        existing = db.query(CurriculumProgram).count()
        if existing >= 5:
            print("Curriculum already seeded — updating...")
            _update_alphabet_audio(db)
            _update_existing_programs(db)
            return

        print("Seeding curriculum programs...")
        for meta in PROGRAMS_META:
            seeder = meta["seeder"]
            fields = {k: v for k, v in meta.items() if k != "seeder"}
            program = CurriculumProgram(**fields)
            db.add(program)
            db.flush()
            seeder(db, program)
            db.flush()
            print(f"  ✓ {program.title_fr} ({program.total_units} units)")

        db.commit()
        print("Curriculum seed complete.")
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_curriculum()
