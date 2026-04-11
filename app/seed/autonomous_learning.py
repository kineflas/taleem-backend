"""
Autonomous Learning seed data — Neuroscience-based Quran vocabulary acquisition.

Contains:
  - 120 most frequent Quran words (40 particles + 60 nouns + 20 verbs)
  - 30 essential Arabic roots with derivations
  - 50 Quran collocations/chunks

Run: python -m app.seed.autonomous_learning
Called automatically on startup (idempotent).
"""
from ..database import SessionLocal
from ..models.autonomous_learning import (
    QuranWord, ArabicRoot, QuranChunk,
    WordCategory, ChunkLevel,
)


# ══════════════════════════════════════════════════════════════════════════════
# PART A: PARTICLES (rank 1-40)
# ══════════════════════════════════════════════════════════════════════════════

PARTICLES_DATA = [
    # (rank, arabic, transliteration, translation_fr, translation_en, frequency, module, spatial_position)
    (1, "مِنْ", "min", "de, depuis, parmi", "from, since, among", 3226, 2, "from"),
    (2, "اللَّه", "Allāh", "Allah, Dieu", "Allah, God", 2699, 1, None),  # PROPER_NOUN
    (3, "فِي", "fī", "dans", "in", 1701, 2, "inside"),
    (4, "إِنَّ", "inna", "certes, en vérité", "indeed, verily", 1682, 1, None),
    (5, "عَلَى", "'alā", "sur, contre", "on, upon, against", 1445, 2, "above"),
    (6, "الَّذِي", "al-ladhī", "celui qui (relatif masc.)", "who, which (relative)", 1442, 1, None),
    (7, "لَا", "lā", "ne…pas (négation)", "no, not", 1364, 1, None),
    (8, "مَا", "mā", "ce que, ce qui", "what, that which", 1266, 1, None),
    (9, "إِلَى", "ilā", "vers, jusqu'à", "to, toward, until", 742, 2, "toward"),
    (10, "مَنْ", "man", "celui qui, quiconque", "whoever, who", 606, 1, None),
    (11, "إِنْ", "in", "si (conditionnel)", "if", 578, 1, None),
    (12, "أَنْ", "an", "que (conjonction)", "that", 578, 1, None),
    (13, "إِلَّا", "illā", "sauf, excepté", "except, unless", 558, 1, None),
    (14, "ذَلِكَ", "dhālika", "cela, celui-là", "that", 520, 1, None),
    (15, "عَنْ", "'an", "de, au sujet de", "from, about", 465, 2, "away"),
    (16, "قَدْ", "qad", "certes, déjà", "already, indeed", 406, 1, None),
    (17, "إِذَا", "idhā", "lorsque, quand", "when, if", 405, 1, None),
    (18, "أَنَّ", "anna", "que (complétive)", "that", 362, 1, None),
    (19, "كُلّ", "kull", "tout, chaque", "all, every", 358, 1, None),
    (20, "لَمْ", "lam", "ne…pas (passé)", "did not", 353, 1, None),
    (21, "ثُمَّ", "thumma", "ensuite, puis", "then, moreover", 338, 1, None),
    (22, "هَذَا", "hādhā", "ceci, celui-ci", "this", 317, 1, None),
    (23, "أَوْ", "aw", "ou", "or", 280, 1, None),
    (24, "بَيْنَ", "bayna", "entre", "between", 243, 2, "between"),
    (25, "إِذْ", "idh", "lorsque (passé)", "when", 239, 1, None),
    (26, "أُولَئِكَ", "ulā'ika", "ceux-là", "those", 204, 1, None),
    (27, "قَبْلَ", "qabla", "avant", "before", 197, 2, "before_time"),
    (28, "لَوْ", "law", "si (irréel)", "if (hypothetical)", 184, 1, None),
    (29, "عِنْدَ", "'inda", "auprès de, chez", "at, near, with", 160, 2, "near"),
    (30, "مَعَ", "ma'a", "avec", "with", 159, 2, "with"),
    (31, "بَعْضَ", "ba'ḍ", "quelques, certains", "some, part of", 157, 1, None),
    (32, "لَمَّا", "lammā", "lorsque", "when", 156, 1, None),
    (33, "أَيُّهَا", "ayyuhā", "ô ! (vocatif)", "O! (vocative)", 153, 1, None),
    (34, "غَيْرَ", "ghayra", "autre que, sauf", "other than, except", 144, 1, None),
    (35, "أَمْ", "am", "ou bien", "or rather", 137, 1, None),
    (36, "دُونَ", "dūna", "en dessous de, sans", "below, without", 135, 2, "below"),
    (37, "بَعْدَ", "ba'da", "après", "after", 133, 2, "after_time"),
    (38, "لَعَلَّ", "la'alla", "peut-être que, afin que", "perhaps, so that", 123, 1, None),
    (39, "بَلْ", "bal", "plutôt, mais au contraire", "rather, but", 122, 1, None),
    (40, "حَتَّى", "ḥattā", "jusqu'à ce que", "until", 95, 1, None),
]


# ══════════════════════════════════════════════════════════════════════════════
# PART B: NOUNS (rank 41-100)
# ══════════════════════════════════════════════════════════════════════════════

NOUNS_DATA = [
    # (rank, arabic, transliteration, translation_fr, translation_en, frequency, category)
    (41, "رَبّ", "rabb", "Seigneur", "Lord", 975, WordCategory.NOUN),
    (42, "أَرْض", "arḍ", "terre", "earth, land", 461, WordCategory.NOUN),
    (43, "قَوْم", "qawm", "peuple", "people, nation", 383, WordCategory.NOUN),
    (44, "آيَة", "āya", "signe, verset", "sign, verse", 382, WordCategory.NOUN),
    (45, "رَسُول", "rasūl", "messager", "messenger", 332, WordCategory.NOUN),
    (46, "يَوْم", "yawm", "jour", "day", 325, WordCategory.NOUN),
    (47, "عَذَاب", "'adhāb", "châtiment", "punishment, torment", 322, WordCategory.NOUN),
    (48, "سَمَاء", "samā'", "ciel", "sky, heaven", 310, WordCategory.NOUN),
    (49, "نَفْس", "nafs", "âme, soi-même", "soul, self", 295, WordCategory.NOUN),
    (50, "شَيْء", "shay'", "chose", "thing", 283, WordCategory.NOUN),
    (51, "كِتَاب", "kitāb", "livre", "book", 260, WordCategory.NOUN),
    (52, "حَقّ", "ḥaqq", "vérité, droit", "truth, right", 242, WordCategory.NOUN),
    (53, "نَاس", "nās", "gens, humains", "people, mankind", 241, WordCategory.NOUN),
    (54, "مُؤْمِن", "mu'min", "croyant", "believer", 195, WordCategory.NOUN),
    (55, "سَبِيل", "sabīl", "chemin, voie", "way, path", 176, WordCategory.NOUN),
    (56, "أَمْر", "amr", "ordre, affaire", "command, matter", 166, WordCategory.NOUN),
    (57, "خَيْر", "khayr", "bien, meilleur", "good, better", 148, WordCategory.NOUN),
    (58, "إِلَه", "ilāh", "divinité", "deity, god", 147, WordCategory.NOUN),
    (59, "نَار", "nār", "feu (enfer)", "fire, hellfire", 145, WordCategory.NOUN),
    (60, "مُوسَى", "Mūsā", "Moïse", "Moses", 136, WordCategory.PROPER_NOUN),
    (61, "قَلْب", "qalb", "cœur", "heart", 132, WordCategory.NOUN),
    (62, "عَبْد", "'abd", "serviteur", "servant, slave", 131, WordCategory.NOUN),
    (63, "أَهْل", "ahl", "famille, gens de", "family, people of", 127, WordCategory.NOUN),
    (64, "يَد", "yad", "main", "hand", 120, WordCategory.NOUN),
    (65, "كَافِر", "kāfir", "mécréant", "disbeliever", 119, WordCategory.NOUN),
    (66, "رَحْمَة", "raḥma", "miséricorde", "mercy", 114, WordCategory.NOUN),
    (67, "آخِر", "ākhir", "autre, dernier", "other, last", 133, WordCategory.NOUN),
    (68, "عِلْم", "'ilm", "science, savoir", "knowledge, science", 105, WordCategory.NOUN),
    (69, "أَجْر", "ajr", "récompense", "reward", 105, WordCategory.NOUN),
    (70, "ظَالِم", "ẓālim", "injuste", "wrongdoer, unjust", 105, WordCategory.NOUN),
    (71, "عَظِيم", "'aẓīm", "immense", "great, mighty", 104, WordCategory.NOUN),
    (72, "عَلِيم", "'alīm", "Omniscient", "All-Knowing", 101, WordCategory.NOUN),
    (73, "جَنَّة", "janna", "paradis, jardin", "paradise, garden", 96, WordCategory.NOUN),
    (74, "قَوْل", "qawl", "parole", "saying, speech", 92, WordCategory.NOUN),
    (75, "دِين", "dīn", "religion, jugement", "religion, judgment", 92, WordCategory.NOUN),
    (76, "ذُو", "dhū", "possesseur de", "possessor of", 90, WordCategory.NOUN),
    (77, "مَلَك", "malak", "ange", "angel", 88, WordCategory.NOUN),
    (78, "مَثَل", "mathal", "parabole, exemple", "parable, example", 87, WordCategory.NOUN),
    (79, "رَحِيم", "raḥīm", "Miséricordieux", "Most Merciful", 112, WordCategory.NOUN),
    (80, "مَال", "māl", "bien(s), richesse", "wealth, property", 86, WordCategory.NOUN),
    (81, "وَلِيّ", "waliyy", "protecteur, allié", "protector, ally", 86, WordCategory.NOUN),
    (82, "هُدًى", "hudan", "guidance", "guidance", 85, WordCategory.NOUN),
    (83, "حَكِيم", "ḥakīm", "sage", "wise", 84, WordCategory.NOUN),
    (84, "فَضْل", "faḍl", "grâce, faveur", "grace, bounty", 84, WordCategory.NOUN),
    (85, "صَلَاة", "ṣalāt", "prière", "prayer", 83, WordCategory.NOUN),
    (86, "لَيْل", "layl", "nuit", "night", 82, WordCategory.NOUN),
    (87, "اِبْن", "ibn", "fils", "son", 80, WordCategory.NOUN),
    (88, "شَيْطَان", "shayṭān", "Satan, diable", "Satan, devil", 80, WordCategory.NOUN),
    (89, "أَصْحَاب", "aṣḥāb", "compagnons, gens de", "companions, people of", 78, WordCategory.NOUN),
    (90, "أَكْثَر", "akthar", "la plupart", "most, majority", 78, WordCategory.NOUN),
    (91, "جَهَنَّم", "jahannam", "la Géhenne, l'Enfer", "Hell, Gehenna", 77, WordCategory.NOUN),
    (92, "حَيَاة", "ḥayāt", "vie", "life", 76, WordCategory.NOUN),
    (93, "ذِكْر", "dhikr", "rappel, évocation", "remembrance, mention", 76, WordCategory.NOUN),
    (94, "نَهَار", "nahār", "jour (lumière)", "daytime, daylight", 74, WordCategory.NOUN),
    (95, "عِيسَى", "'Īsā", "Jésus", "Jesus", 73, WordCategory.PROPER_NOUN),
    (96, "مَاء", "mā'", "eau", "water", 63, WordCategory.NOUN),
    (97, "نُور", "nūr", "lumière", "light", 43, WordCategory.NOUN),
    (98, "فَوْقَ", "fawqa", "au-dessus", "above", 50, WordCategory.NOUN),
    (99, "سُورَة", "sūrah", "chapitre du Coran", "chapter of Quran", 56, WordCategory.NOUN),
    (100, "تَوْرَاة", "tawrāh", "Thora", "Torah", 42, WordCategory.NOUN),
]


# ══════════════════════════════════════════════════════════════════════════════
# PART C: VERBS (rank 101-120)
# ══════════════════════════════════════════════════════════════════════════════

VERBS_DATA = [
    # (rank, arabic, transliteration, translation_fr, translation_en, frequency)
    (101, "قَالَ", "qāla", "dire", "to say", 1618),
    (102, "كَانَ", "kāna", "être", "to be", 1358),
    (103, "آمَنَ", "āmana", "croire", "to believe", 537),
    (104, "عَلِمَ", "'alima", "savoir", "to know", 382),
    (105, "جَعَلَ", "ja'ala", "faire, rendre", "to make, render", 340),
    (106, "كَفَرَ", "kafara", "mécroire, nier", "to disbelieve, deny", 289),
    (107, "جَاءَ", "jā'a", "venir", "to come", 278),
    (108, "عَمِلَ", "'amila", "œuvrer, faire", "to do, work", 276),
    (109, "آتَى", "ātā", "donner, accorder", "to give, grant", 271),
    (110, "رَأَى", "ra'ā", "voir", "to see", 271),
    (111, "أَتَى", "atā", "venir, apporter", "to come, bring", 264),
    (112, "شَاءَ", "shā'a", "vouloir", "to will, wish", 236),
    (113, "خَلَقَ", "khalaqa", "créer", "to create", 184),
    (114, "أَنْزَلَ", "anzala", "révéler, descendre", "to reveal, send down", 183),
    (115, "كَذَّبَ", "kadhdhaba", "démentir", "to deny, belie", 176),
    (116, "دَعَا", "da'ā", "invoquer, appeler", "to call, invoke", 170),
    (117, "اتَّقَى", "ittaqā", "craindre (Allah)", "to fear (God)", 166),
    (118, "هَدَى", "hadā", "guider", "to guide", 144),
    (119, "أَرَادَ", "arāda", "vouloir", "to want, intend", 139),
    (120, "اتَّبَعَ", "ittaba'a", "suivre", "to follow", 136),
]


# ══════════════════════════════════════════════════════════════════════════════
# PART D: ARABIC ROOTS (30 roots with derivations)
# ══════════════════════════════════════════════════════════════════════════════

ROOTS_DATA = [
    {
        "rank": 1,
        "root_letters": "ك-ت-ب",
        "root_bare": "كتب",
        "meaning_fr": "écrire",
        "meaning_en": "to write",
        "derivations": [
            {"arabic": "كِتَاب", "meaning_fr": "livre", "meaning_en": "book"},
            {"arabic": "كَاتِب", "meaning_fr": "écrivain", "meaning_en": "writer"},
            {"arabic": "مَكْتُوب", "meaning_fr": "écrit", "meaning_en": "written"},
            {"arabic": "كُتُب", "meaning_fr": "livres", "meaning_en": "books"},
        ]
    },
    {
        "rank": 2,
        "root_letters": "ع-ل-م",
        "root_bare": "علم",
        "meaning_fr": "savoir",
        "meaning_en": "to know",
        "derivations": [
            {"arabic": "عِلْم", "meaning_fr": "science", "meaning_en": "knowledge"},
            {"arabic": "عَالِم", "meaning_fr": "savant", "meaning_en": "scholar"},
            {"arabic": "مُعَلِّم", "meaning_fr": "enseignant", "meaning_en": "teacher"},
            {"arabic": "عَلِيم", "meaning_fr": "Omniscient", "meaning_en": "All-Knowing"},
        ]
    },
    {
        "rank": 3,
        "root_letters": "ق-و-ل",
        "root_bare": "قول",
        "meaning_fr": "dire",
        "meaning_en": "to say",
        "derivations": [
            {"arabic": "قَوْل", "meaning_fr": "parole", "meaning_en": "saying"},
            {"arabic": "قَائِل", "meaning_fr": "celui qui dit", "meaning_en": "speaker"},
            {"arabic": "مَقُول", "meaning_fr": "dit", "meaning_en": "said"},
        ]
    },
    {
        "rank": 4,
        "root_letters": "ع-م-ل",
        "root_bare": "عمل",
        "meaning_fr": "faire",
        "meaning_en": "to do/work",
        "derivations": [
            {"arabic": "عَمَل", "meaning_fr": "action", "meaning_en": "deed"},
            {"arabic": "عَامِل", "meaning_fr": "travailleur", "meaning_en": "worker"},
            {"arabic": "مَعْمُول", "meaning_fr": "fait", "meaning_en": "done"},
        ]
    },
    {
        "rank": 5,
        "root_letters": "ا-م-ن",
        "root_bare": "امن",
        "meaning_fr": "être en sécurité",
        "meaning_en": "to be safe",
        "derivations": [
            {"arabic": "أَمْن", "meaning_fr": "sécurité", "meaning_en": "security"},
            {"arabic": "إِيمَان", "meaning_fr": "foi", "meaning_en": "faith"},
            {"arabic": "مُؤْمِن", "meaning_fr": "croyant", "meaning_en": "believer"},
            {"arabic": "أَمِين", "meaning_fr": "fidèle", "meaning_en": "trustworthy"},
        ]
    },
    {
        "rank": 6,
        "root_letters": "ر-ح-م",
        "root_bare": "رحم",
        "meaning_fr": "faire miséricorde",
        "meaning_en": "to have mercy",
        "derivations": [
            {"arabic": "رَحْمَة", "meaning_fr": "miséricorde", "meaning_en": "mercy"},
            {"arabic": "رَحِيم", "meaning_fr": "Miséricordieux", "meaning_en": "Merciful"},
            {"arabic": "رَحْمَان", "meaning_fr": "Tout-Miséricordieux", "meaning_en": "Most Gracious"},
        ]
    },
    {
        "rank": 7,
        "root_letters": "خ-ل-ق",
        "root_bare": "خلق",
        "meaning_fr": "créer",
        "meaning_en": "to create",
        "derivations": [
            {"arabic": "خَلْق", "meaning_fr": "création", "meaning_en": "creation"},
            {"arabic": "خَالِق", "meaning_fr": "Créateur", "meaning_en": "Creator"},
            {"arabic": "مَخْلُوق", "meaning_fr": "créature", "meaning_en": "creature"},
        ]
    },
    {
        "rank": 8,
        "root_letters": "ح-ق-ق",
        "root_bare": "حقق",
        "meaning_fr": "être vrai",
        "meaning_en": "to be true",
        "derivations": [
            {"arabic": "حَقّ", "meaning_fr": "vérité", "meaning_en": "truth"},
            {"arabic": "حَقِيقَة", "meaning_fr": "réalité", "meaning_en": "reality"},
            {"arabic": "تَحْقِيق", "meaning_fr": "réalisation", "meaning_en": "verification"},
        ]
    },
    {
        "rank": 9,
        "root_letters": "ج-ع-ل",
        "root_bare": "جعل",
        "meaning_fr": "faire/rendre",
        "meaning_en": "to make/render",
        "derivations": [
            {"arabic": "جَعْل", "meaning_fr": "action de faire", "meaning_en": "making"},
            {"arabic": "جَاعِل", "meaning_fr": "celui qui fait", "meaning_en": "maker"},
        ]
    },
    {
        "rank": 10,
        "root_letters": "ه-د-ي",
        "root_bare": "هدي",
        "meaning_fr": "guider",
        "meaning_en": "to guide",
        "derivations": [
            {"arabic": "هُدًى", "meaning_fr": "guidance", "meaning_en": "guidance"},
            {"arabic": "هَادِي", "meaning_fr": "guide", "meaning_en": "guide"},
            {"arabic": "مُهْتَدِي", "meaning_fr": "bien guidé", "meaning_en": "rightly guided"},
        ]
    },
    {
        "rank": 11,
        "root_letters": "ن-ز-ل",
        "root_bare": "نزل",
        "meaning_fr": "descendre",
        "meaning_en": "to descend",
        "derivations": [
            {"arabic": "نُزُول", "meaning_fr": "descente", "meaning_en": "descent"},
            {"arabic": "تَنْزِيل", "meaning_fr": "révélation", "meaning_en": "revelation"},
            {"arabic": "مُنَزَّل", "meaning_fr": "révélé", "meaning_en": "revealed"},
        ]
    },
    {
        "rank": 12,
        "root_letters": "س-ل-م",
        "root_bare": "سلم",
        "meaning_fr": "être en paix",
        "meaning_en": "to be at peace",
        "derivations": [
            {"arabic": "سَلَام", "meaning_fr": "paix", "meaning_en": "peace"},
            {"arabic": "إِسْلَام", "meaning_fr": "soumission", "meaning_en": "Islam"},
            {"arabic": "مُسْلِم", "meaning_fr": "soumis", "meaning_en": "Muslim"},
        ]
    },
    {
        "rank": 13,
        "root_letters": "ك-ف-ر",
        "root_bare": "كفر",
        "meaning_fr": "couvrir/nier",
        "meaning_en": "to cover/deny",
        "derivations": [
            {"arabic": "كُفْر", "meaning_fr": "mécréance", "meaning_en": "disbelief"},
            {"arabic": "كَافِر", "meaning_fr": "mécréant", "meaning_en": "disbeliever"},
            {"arabic": "كُفَّار", "meaning_fr": "mécréants", "meaning_en": "disbelievers"},
        ]
    },
    {
        "rank": 14,
        "root_letters": "ج-ن-ن",
        "root_bare": "جنن",
        "meaning_fr": "cacher/couvrir",
        "meaning_en": "to hide/cover",
        "derivations": [
            {"arabic": "جَنَّة", "meaning_fr": "jardin/paradis", "meaning_en": "garden/paradise"},
            {"arabic": "جِنّ", "meaning_fr": "djinns", "meaning_en": "jinn"},
            {"arabic": "مَجْنُون", "meaning_fr": "fou", "meaning_en": "possessed"},
        ]
    },
    {
        "rank": 15,
        "root_letters": "ن-ف-س",
        "root_bare": "نفس",
        "meaning_fr": "âme/souffle",
        "meaning_en": "soul/breath",
        "derivations": [
            {"arabic": "نَفْس", "meaning_fr": "âme", "meaning_en": "soul"},
            {"arabic": "تَنَفُّس", "meaning_fr": "respiration", "meaning_en": "breathing"},
            {"arabic": "أَنْفُس", "meaning_fr": "âmes", "meaning_en": "souls"},
        ]
    },
    {
        "rank": 16,
        "root_letters": "ظ-ل-م",
        "root_bare": "ظلم",
        "meaning_fr": "opprimer",
        "meaning_en": "to oppress",
        "derivations": [
            {"arabic": "ظُلْم", "meaning_fr": "injustice", "meaning_en": "injustice"},
            {"arabic": "ظَالِم", "meaning_fr": "injuste", "meaning_en": "oppressor"},
            {"arabic": "ظُلُمَات", "meaning_fr": "ténèbres", "meaning_en": "darkness"},
        ]
    },
    {
        "rank": 17,
        "root_letters": "ع-ذ-ب",
        "root_bare": "عذب",
        "meaning_fr": "châtier",
        "meaning_en": "to punish",
        "derivations": [
            {"arabic": "عَذَاب", "meaning_fr": "châtiment", "meaning_en": "punishment"},
            {"arabic": "مُعَذَّب", "meaning_fr": "châtié", "meaning_en": "punished"},
        ]
    },
    {
        "rank": 18,
        "root_letters": "ش-ر-ك",
        "root_bare": "شرك",
        "meaning_fr": "associer",
        "meaning_en": "to associate",
        "derivations": [
            {"arabic": "شِرْك", "meaning_fr": "associationnisme", "meaning_en": "polytheism"},
            {"arabic": "مُشْرِك", "meaning_fr": "associateur", "meaning_en": "polytheist"},
            {"arabic": "شَرِيك", "meaning_fr": "partenaire", "meaning_en": "partner"},
        ]
    },
    {
        "rank": 19,
        "root_letters": "س-ب-ل",
        "root_bare": "سبل",
        "meaning_fr": "chemin",
        "meaning_en": "way/path",
        "derivations": [
            {"arabic": "سَبِيل", "meaning_fr": "chemin", "meaning_en": "way"},
            {"arabic": "سُبُل", "meaning_fr": "chemins", "meaning_en": "ways"},
        ]
    },
    {
        "rank": 20,
        "root_letters": "د-ع-و",
        "root_bare": "دعو",
        "meaning_fr": "appeler",
        "meaning_en": "to call",
        "derivations": [
            {"arabic": "دُعَاء", "meaning_fr": "invocation", "meaning_en": "supplication"},
            {"arabic": "دَاعِي", "meaning_fr": "appeleur", "meaning_en": "caller"},
            {"arabic": "دَعْوَة", "meaning_fr": "appel", "meaning_en": "call"},
        ]
    },
    {
        "rank": 21,
        "root_letters": "ص-ل-ح",
        "root_bare": "صلح",
        "meaning_fr": "être bon",
        "meaning_en": "to be good",
        "derivations": [
            {"arabic": "صَالِح", "meaning_fr": "vertueux", "meaning_en": "righteous"},
            {"arabic": "إِصْلَاح", "meaning_fr": "réforme", "meaning_en": "reform"},
            {"arabic": "صُلْح", "meaning_fr": "paix", "meaning_en": "reconciliation"},
        ]
    },
    {
        "rank": 22,
        "root_letters": "ح-ك-م",
        "root_bare": "حكم",
        "meaning_fr": "juger",
        "meaning_en": "to judge",
        "derivations": [
            {"arabic": "حُكْم", "meaning_fr": "jugement", "meaning_en": "judgment"},
            {"arabic": "حَكِيم", "meaning_fr": "sage", "meaning_en": "wise"},
            {"arabic": "حَاكِم", "meaning_fr": "juge", "meaning_en": "judge"},
        ]
    },
    {
        "rank": 23,
        "root_letters": "ق-ل-ب",
        "root_bare": "قلب",
        "meaning_fr": "retourner",
        "meaning_en": "to turn over",
        "derivations": [
            {"arabic": "قَلْب", "meaning_fr": "cœur", "meaning_en": "heart"},
            {"arabic": "تَقَلُّب", "meaning_fr": "changement", "meaning_en": "turning"},
            {"arabic": "قُلُوب", "meaning_fr": "cœurs", "meaning_en": "hearts"},
        ]
    },
    {
        "rank": 24,
        "root_letters": "ن-ص-ر",
        "root_bare": "نصر",
        "meaning_fr": "aider/secourir",
        "meaning_en": "to help/support",
        "derivations": [
            {"arabic": "نَصْر", "meaning_fr": "victoire", "meaning_en": "victory"},
            {"arabic": "نَاصِر", "meaning_fr": "aide", "meaning_en": "helper"},
            {"arabic": "أَنْصَار", "meaning_fr": "partisans", "meaning_en": "supporters"},
        ]
    },
    {
        "rank": 25,
        "root_letters": "ف-ض-ل",
        "root_bare": "فضل",
        "meaning_fr": "être supérieur",
        "meaning_en": "to be superior",
        "derivations": [
            {"arabic": "فَضْل", "meaning_fr": "grâce", "meaning_en": "bounty"},
            {"arabic": "فَاضِل", "meaning_fr": "vertueux", "meaning_en": "virtuous"},
            {"arabic": "تَفْضِيل", "meaning_fr": "préférence", "meaning_en": "preference"},
        ]
    },
    {
        "rank": 26,
        "root_letters": "ذ-ك-ر",
        "root_bare": "ذكر",
        "meaning_fr": "se rappeler",
        "meaning_en": "to remember",
        "derivations": [
            {"arabic": "ذِكْر", "meaning_fr": "rappel", "meaning_en": "remembrance"},
            {"arabic": "ذَاكِر", "meaning_fr": "celui qui se rappelle", "meaning_en": "one who remembers"},
            {"arabic": "تَذْكِرَة", "meaning_fr": "rappel", "meaning_en": "reminder"},
        ]
    },
    {
        "rank": 27,
        "root_letters": "ح-ي-ي",
        "root_bare": "حيي",
        "meaning_fr": "vivre",
        "meaning_en": "to live",
        "derivations": [
            {"arabic": "حَيَاة", "meaning_fr": "vie", "meaning_en": "life"},
            {"arabic": "حَيّ", "meaning_fr": "vivant", "meaning_en": "alive"},
            {"arabic": "إِحْيَاء", "meaning_fr": "résurrection", "meaning_en": "revival"},
        ]
    },
    {
        "rank": 28,
        "root_letters": "ب-ع-ث",
        "root_bare": "بعث",
        "meaning_fr": "envoyer/ressusciter",
        "meaning_en": "to send/resurrect",
        "derivations": [
            {"arabic": "بَعْث", "meaning_fr": "résurrection", "meaning_en": "resurrection"},
            {"arabic": "مَبْعُوث", "meaning_fr": "envoyé", "meaning_en": "sent one"},
            {"arabic": "بَاعِث", "meaning_fr": "celui qui ressuscite", "meaning_en": "resurrector"},
        ]
    },
    {
        "rank": 29,
        "root_letters": "ش-ه-د",
        "root_bare": "شهد",
        "meaning_fr": "témoigner",
        "meaning_en": "to witness",
        "derivations": [
            {"arabic": "شَهَادَة", "meaning_fr": "témoignage", "meaning_en": "testimony"},
            {"arabic": "شَاهِد", "meaning_fr": "témoin", "meaning_en": "witness"},
            {"arabic": "شَهِيد", "meaning_fr": "martyr", "meaning_en": "martyr"},
        ]
    },
    {
        "rank": 30,
        "root_letters": "ع-ب-د",
        "root_bare": "عبد",
        "meaning_fr": "adorer",
        "meaning_en": "to worship",
        "derivations": [
            {"arabic": "عِبَادَة", "meaning_fr": "adoration", "meaning_en": "worship"},
            {"arabic": "عَبْد", "meaning_fr": "serviteur", "meaning_en": "servant"},
            {"arabic": "مَعْبُود", "meaning_fr": "adoré", "meaning_en": "worshipped"},
            {"arabic": "عِبَاد", "meaning_fr": "serviteurs", "meaning_en": "servants"},
        ]
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# PART E: QURAN CHUNKS (50 collocations at 3 levels)
# ══════════════════════════════════════════════════════════════════════════════

CHUNKS_DATA = [
    # PAIR level (1-20)
    {"rank": 1, "level": ChunkLevel.PAIR, "arabic": "فِي الأَرْضِ", "transliteration": "fī al-arḍ", "translation_fr": "sur la terre", "translation_en": "on the earth", "surah": 2, "verse": 11},
    {"rank": 2, "level": ChunkLevel.PAIR, "arabic": "مِنَ السَّمَاءِ", "transliteration": "min al-samā'", "translation_fr": "du ciel", "translation_en": "from the sky", "surah": 2, "verse": 22},
    {"rank": 3, "level": ChunkLevel.PAIR, "arabic": "إِلَى اللَّهِ", "transliteration": "ilā Allāh", "translation_fr": "vers Allah", "translation_en": "to Allah", "surah": 2, "verse": 46},
    {"rank": 4, "level": ChunkLevel.PAIR, "arabic": "عَلَى كُلِّ", "transliteration": "'alā kull", "translation_fr": "sur tout", "translation_en": "upon every", "surah": 2, "verse": 20},
    {"rank": 5, "level": ChunkLevel.PAIR, "arabic": "فِي سَبِيلِ", "transliteration": "fī sabīl", "translation_fr": "dans le chemin", "translation_en": "in the way", "surah": 2, "verse": 154},
    {"rank": 6, "level": ChunkLevel.PAIR, "arabic": "مِنْ قَبْلِ", "transliteration": "min qabl", "translation_fr": "d'avant", "translation_en": "from before", "surah": 2, "verse": 25},
    {"rank": 7, "level": ChunkLevel.PAIR, "arabic": "بَيْنَ يَدَيْهِ", "transliteration": "bayna yadayh", "translation_fr": "devant lui", "translation_en": "before him", "surah": 2, "verse": 255},
    {"rank": 8, "level": ChunkLevel.PAIR, "arabic": "عِنْدَ رَبِّهِ", "transliteration": "'inda rabbih", "translation_fr": "auprès de son Seigneur", "translation_en": "with his Lord", "surah": 2, "verse": 112},
    {"rank": 9, "level": ChunkLevel.PAIR, "arabic": "مِنْ دُونِ", "transliteration": "min dūn", "translation_fr": "en dehors de", "translation_en": "besides, other than", "surah": 2, "verse": 23},
    {"rank": 10, "level": ChunkLevel.PAIR, "arabic": "بَعْدَ ذَلِكَ", "transliteration": "ba'da dhālika", "translation_fr": "après cela", "translation_en": "after that", "surah": 2, "verse": 52},
    {"rank": 11, "level": ChunkLevel.PAIR, "arabic": "عَنِ الدِّينِ", "transliteration": "'an al-dīn", "translation_fr": "au sujet de la religion", "translation_en": "about religion", "surah": 2, "verse": 217},
    {"rank": 12, "level": ChunkLevel.PAIR, "arabic": "فِي الكِتَابِ", "transliteration": "fī al-kitāb", "translation_fr": "dans le Livre", "translation_en": "in the Book", "surah": 2, "verse": 2},
    {"rank": 13, "level": ChunkLevel.PAIR, "arabic": "إِلَى يَوْمِ", "transliteration": "ilā yawm", "translation_fr": "jusqu'au jour", "translation_en": "until the day", "surah": 2, "verse": 113},
    {"rank": 14, "level": ChunkLevel.PAIR, "arabic": "عَلَى النَّاسِ", "transliteration": "'alā al-nās", "translation_fr": "sur les gens", "translation_en": "upon people", "surah": 2, "verse": 143},
    {"rank": 15, "level": ChunkLevel.PAIR, "arabic": "مَعَ الصَّابِرِينَ", "transliteration": "ma'a al-ṣābirīn", "translation_fr": "avec les patients", "translation_en": "with the patient ones", "surah": 2, "verse": 153},
    {"rank": 16, "level": ChunkLevel.PAIR, "arabic": "فِي قُلُوبِهِمْ", "transliteration": "fī qulūbihim", "translation_fr": "dans leurs cœurs", "translation_en": "in their hearts", "surah": 2, "verse": 10},
    {"rank": 17, "level": ChunkLevel.PAIR, "arabic": "بِيَدِهِ", "transliteration": "bi-yadih", "translation_fr": "dans sa main", "translation_en": "in his hand", "surah": 2, "verse": 255},
    {"rank": 18, "level": ChunkLevel.PAIR, "arabic": "عَلَى الظَّالِمِينَ", "transliteration": "'alā al-ẓālimīn", "translation_fr": "sur les injustes", "translation_en": "upon the wrongdoers", "surah": 2, "verse": 35},
    {"rank": 19, "level": ChunkLevel.PAIR, "arabic": "مِنَ النَّارِ", "transliteration": "min al-nār", "translation_fr": "du feu", "translation_en": "from the fire", "surah": 2, "verse": 167},
    {"rank": 20, "level": ChunkLevel.PAIR, "arabic": "إِلَى الحَقِّ", "transliteration": "ilā al-ḥaqq", "translation_fr": "vers la vérité", "translation_en": "to the truth", "surah": 10, "verse": 35},

    # TRIPLET level (21-35)
    {"rank": 21, "level": ChunkLevel.TRIPLET, "arabic": "فِي سَبِيلِ اللَّهِ", "transliteration": "fī sabīl Allāh", "translation_fr": "dans le chemin d'Allah", "translation_en": "in the way of Allah", "surah": 2, "verse": 154},
    {"rank": 22, "level": ChunkLevel.TRIPLET, "arabic": "بِإِذْنِ اللَّهِ", "transliteration": "bi-idhn Allāh", "translation_fr": "avec la permission d'Allah", "translation_en": "by Allah's permission", "surah": 2, "verse": 97},
    {"rank": 23, "level": ChunkLevel.TRIPLET, "arabic": "مِنْ عِنْدِ اللَّهِ", "transliteration": "min 'ind Allāh", "translation_fr": "de la part d'Allah", "translation_en": "from Allah", "surah": 2, "verse": 89},
    {"rank": 24, "level": ChunkLevel.TRIPLET, "arabic": "عَلَى قَوْمِهِ", "transliteration": "'alā qawmih", "translation_fr": "sur son peuple", "translation_en": "upon his people", "surah": 7, "verse": 59},
    {"rank": 25, "level": ChunkLevel.TRIPLET, "arabic": "فِي قَلْبِهِ", "transliteration": "fī qalbih", "translation_fr": "dans son cœur", "translation_en": "in his heart", "surah": 2, "verse": 10},
    {"rank": 26, "level": ChunkLevel.TRIPLET, "arabic": "إِلَى رَبِّكُمْ", "transliteration": "ilā rabbikum", "translation_fr": "vers votre Seigneur", "translation_en": "to your Lord", "surah": 2, "verse": 28},
    {"rank": 27, "level": ChunkLevel.TRIPLET, "arabic": "مِنْ بَيْنِ يَدَيْهِ", "transliteration": "min bayn yadayh", "translation_fr": "devant lui", "translation_en": "from before him", "surah": 2, "verse": 255},
    {"rank": 28, "level": ChunkLevel.TRIPLET, "arabic": "عِنْدَ رَبِّهِمْ", "transliteration": "'inda rabbihim", "translation_fr": "auprès de leur Seigneur", "translation_en": "with their Lord", "surah": 2, "verse": 112},
    {"rank": 29, "level": ChunkLevel.TRIPLET, "arabic": "مَعَ الَّذِينَ آمَنُوا", "transliteration": "ma'a alladhīna āmanū", "translation_fr": "avec ceux qui croient", "translation_en": "with those who believe", "surah": 2, "verse": 14},
    {"rank": 30, "level": ChunkLevel.TRIPLET, "arabic": "بَيْنَ أَيْدِيكُمْ", "transliteration": "bayna aydīkum", "translation_fr": "devant vous", "translation_en": "before you", "surah": 2, "verse": 66},
    {"rank": 31, "level": ChunkLevel.TRIPLET, "arabic": "عَلَى كُلِّ شَيْءٍ", "transliteration": "'alā kull shay'", "translation_fr": "sur toute chose", "translation_en": "over all things", "surah": 2, "verse": 20},
    {"rank": 32, "level": ChunkLevel.TRIPLET, "arabic": "فِي الحَيَاةِ الدُّنْيَا", "transliteration": "fī al-ḥayāt al-dunyā", "translation_fr": "dans la vie d'ici-bas", "translation_en": "in the worldly life", "surah": 2, "verse": 85},
    {"rank": 33, "level": ChunkLevel.TRIPLET, "arabic": "مِنْ دُونِ اللَّهِ", "transliteration": "min dūn Allāh", "translation_fr": "en dehors d'Allah", "translation_en": "besides Allah", "surah": 2, "verse": 23},
    {"rank": 34, "level": ChunkLevel.TRIPLET, "arabic": "إِلَى النَّاسِ", "transliteration": "ilā al-nās", "translation_fr": "vers les gens", "translation_en": "to the people", "surah": 2, "verse": 143},
    {"rank": 35, "level": ChunkLevel.TRIPLET, "arabic": "عَنْ سَبِيلِ اللَّهِ", "transliteration": "'an sabīl Allāh", "translation_fr": "du chemin d'Allah", "translation_en": "from the way of Allah", "surah": 2, "verse": 217},

    # SEGMENT level (36-50)
    {"rank": 36, "level": ChunkLevel.SEGMENT, "arabic": "وَفِي الأَرْضِ آيَاتٌ", "transliteration": "wa-fī al-arḍ āyāt", "translation_fr": "et sur la terre il y a des signes", "translation_en": "and on the earth are signs", "surah": 51, "verse": 20},
    {"rank": 37, "level": ChunkLevel.SEGMENT, "arabic": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ", "transliteration": "bismi Allāh al-Raḥmān al-Raḥīm", "translation_fr": "Au nom d'Allah le Tout-Miséricordieux le Très-Miséricordieux", "translation_en": "In the name of Allah the Most Gracious the Most Merciful", "surah": 1, "verse": 1},
    {"rank": 38, "level": ChunkLevel.SEGMENT, "arabic": "الحَمْدُ لِلَّهِ رَبِّ العَالَمِينَ", "transliteration": "al-ḥamdu li-Allāh rabb al-'ālamīn", "translation_fr": "Louange à Allah Seigneur des mondes", "translation_en": "Praise be to Allah Lord of the worlds", "surah": 1, "verse": 2},
    {"rank": 39, "level": ChunkLevel.SEGMENT, "arabic": "إِنَّ اللَّهَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ", "transliteration": "inna Allāh 'alā kull shay' qadīr", "translation_fr": "Certes Allah est sur toute chose Puissant", "translation_en": "Indeed Allah is over all things competent", "surah": 2, "verse": 20},
    {"rank": 40, "level": ChunkLevel.SEGMENT, "arabic": "وَاللَّهُ بِكُلِّ شَيْءٍ عَلِيمٌ", "transliteration": "wa-Allāh bi-kull shay' 'alīm", "translation_fr": "et Allah de toute chose est Omniscient", "translation_en": "and Allah is Knowing of all things", "surah": 2, "verse": 282},
    {"rank": 41, "level": ChunkLevel.SEGMENT, "arabic": "إِنَّ فِي ذَلِكَ لَآيَاتٍ", "transliteration": "inna fī dhālika la-āyāt", "translation_fr": "certes en cela il y a des signes", "translation_en": "indeed in that are signs", "surah": 2, "verse": 164},
    {"rank": 42, "level": ChunkLevel.SEGMENT, "arabic": "وَمَا أَنْزَلَ مِنَ السَّمَاءِ مِنْ مَاءٍ", "transliteration": "wa-mā anzala min al-samā' min mā'", "translation_fr": "et ce qu'Il a fait descendre du ciel comme eau", "translation_en": "and what He sent down from the sky of water", "surah": 2, "verse": 164},
    {"rank": 43, "level": ChunkLevel.SEGMENT, "arabic": "يَا أَيُّهَا الَّذِينَ آمَنُوا", "transliteration": "yā ayyuhā alladhīna āmanū", "translation_fr": "Ô vous qui croyez", "translation_en": "O you who believe", "surah": 2, "verse": 104},
    {"rank": 44, "level": ChunkLevel.SEGMENT, "arabic": "وَاتَّقُوا يَوْمًا تُرْجَعُونَ فِيهِ إِلَى اللَّهِ", "transliteration": "wa-ittaqū yawman turja'ūna fīhi ilā Allāh", "translation_fr": "et craignez le jour où vous serez ramenés vers Allah", "translation_en": "and fear a day when you will be returned to Allah", "surah": 2, "verse": 281},
    {"rank": 45, "level": ChunkLevel.SEGMENT, "arabic": "أُولَئِكَ لَهُمْ عَذَابٌ عَظِيمٌ", "transliteration": "ulā'ika lahum 'adhāb 'aẓīm", "translation_fr": "ceux-là auront un châtiment immense", "translation_en": "those will have a great punishment", "surah": 2, "verse": 7},
    {"rank": 46, "level": ChunkLevel.SEGMENT, "arabic": "وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ", "transliteration": "wa-huwa 'alā kull shay' qadīr", "translation_fr": "et Il est sur toute chose Puissant", "translation_en": "and He is over all things competent", "surah": 5, "verse": 120},
    {"rank": 47, "level": ChunkLevel.SEGMENT, "arabic": "إِنَّ اللَّهَ غَفُورٌ رَحِيمٌ", "transliteration": "inna Allāh ghafūr raḥīm", "translation_fr": "certes Allah est Pardonneur Miséricordieux", "translation_en": "indeed Allah is Forgiving Merciful", "surah": 2, "verse": 173},
    {"rank": 48, "level": ChunkLevel.SEGMENT, "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً", "transliteration": "rabbanā ātinā fī al-dunyā ḥasanah", "translation_fr": "Notre Seigneur accorde-nous en ce monde un bien", "translation_en": "Our Lord give us in this world good", "surah": 2, "verse": 201},
    {"rank": 49, "level": ChunkLevel.SEGMENT, "arabic": "وَلَا تَقْرَبُوا الفَوَاحِشَ", "transliteration": "wa-lā taqrabū al-fawāḥish", "translation_fr": "et n'approchez pas les turpitudes", "translation_en": "and do not approach immoralities", "surah": 6, "verse": 151},
    {"rank": 50, "level": ChunkLevel.SEGMENT, "arabic": "إِنَّمَا يَخْشَى اللَّهَ مِنْ عِبَادِهِ العُلَمَاءُ", "transliteration": "innamā yakhshā Allāh min 'ibādih al-'ulamā'", "translation_fr": "Seuls les savants parmi Ses serviteurs craignent Allah", "translation_en": "Only those fear Allah from among His servants who have knowledge", "surah": 35, "verse": 28},
]


# ══════════════════════════════════════════════════════════════════════════════
# MAIN SEEDING FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def seed_autonomous_learning(db=None) -> None:
    """
    Seed the autonomous_learning tables idempotently.

    Inserts:
      - 120 QuranWord entries (particles, nouns, verbs)
      - 30 ArabicRoot entries with derivations
      - 50 QuranChunk entries at 3 levels

    Args:
        db: SQLAlchemy Session (auto-created if None)
    """
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        # Check idempotency: if any words exist, skip
        existing_word = db.query(QuranWord).first()
        if existing_word:
            print("Autonomous learning data already seeded — skipping.")
            return

        print("Seeding autonomous learning tables...")

        # ── Seed QuranWord (particles, nouns, verbs) ────────────────────────
        all_words_data = PARTICLES_DATA + NOUNS_DATA + VERBS_DATA

        for rank, arabic, trans, trans_fr, trans_en, freq, *rest in all_words_data:
            # Determine category and module
            if rank <= 40:
                category = WordCategory.PARTICLE
                module = rest[0]  # module from particles
                spatial = rest[1] if len(rest) > 1 else None  # spatial_position
            elif rank <= 100:
                category = rest[0]  # category from nouns (NOUN or PROPER_NOUN)
                module = 1  # nouns all in module 1
                spatial = None
            else:
                category = WordCategory.VERB
                module = 1  # verbs in module 1
                spatial = None

            word = QuranWord(
                rank=rank,
                arabic=arabic,
                transliteration=trans,
                translation_fr=trans_fr,
                translation_en=trans_en,
                category=category,
                frequency=freq,
                module=module,
                spatial_position=spatial,
            )
            db.add(word)

        db.flush()
        print(f"  ✓ Added {len(all_words_data)} QuranWord entries")

        # ── Seed ArabicRoot (30 roots with derivations) ──────────────────────
        for root_data in ROOTS_DATA:
            root = ArabicRoot(
                rank=root_data["rank"],
                root_letters=root_data["root_letters"],
                root_bare=root_data["root_bare"],
                meaning_fr=root_data["meaning_fr"],
                meaning_en=root_data["meaning_en"],
                derivations=root_data["derivations"],
            )
            db.add(root)

        db.flush()
        print(f"  ✓ Added {len(ROOTS_DATA)} ArabicRoot entries")

        # ── Seed QuranChunk (50 collocations) ──────────────────────────────
        for chunk_data in CHUNKS_DATA:
            chunk = QuranChunk(
                rank=chunk_data["rank"],
                level=chunk_data["level"],
                arabic=chunk_data["arabic"],
                transliteration=chunk_data["transliteration"],
                translation_fr=chunk_data["translation_fr"],
                translation_en=chunk_data.get("translation_en"),
                surah_number=chunk_data.get("surah"),
                verse_number=chunk_data.get("verse"),
            )
            db.add(chunk)

        db.flush()
        print(f"  ✓ Added {len(CHUNKS_DATA)} QuranChunk entries")

        # Commit all
        db.commit()
        print("Autonomous learning seed complete.")

    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_autonomous_learning()
