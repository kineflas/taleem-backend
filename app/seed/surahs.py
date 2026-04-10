"""
Seed the surahs table with all 114 surahs of the Quran.
Run: python -m app.seed.surahs
"""
from ..database import SessionLocal
from ..models.quran import Surah

# (surah_number, name_ar, name_fr, name_en, total_verses, juz, is_meccan)
SURAHS_DATA = [
    (1,  "الفاتحة",   "L'Ouverture",             "The Opening",           7,   1,  True),
    (2,  "البقرة",    "La Vache",                 "The Cow",               286, 1,  False),
    (3,  "آل عمران", "La Famille d'Imrân",        "Family of Imran",       200, 3,  False),
    (4,  "النساء",   "Les Femmes",               "The Women",             176, 4,  False),
    (5,  "المائدة",  "La Table Servie",           "The Table Spread",      120, 6,  False),
    (6,  "الأنعام",  "Les Bestiaux",             "The Cattle",            165, 7,  True),
    (7,  "الأعراف",  "Les Murailles",            "The Heights",           206, 8,  True),
    (8,  "الأنفال",  "Le Butin",                 "The Spoils of War",     75,  9,  False),
    (9,  "التوبة",   "Le Repentir",              "The Repentance",        129, 10, False),
    (10, "يونس",     "Jonas",                    "Jonah",                 109, 11, True),
    (11, "هود",      "Houd",                     "Hud",                   123, 11, True),
    (12, "يوسف",     "Joseph",                   "Joseph",                111, 12, True),
    (13, "الرعد",    "Le Tonnerre",              "The Thunder",           43,  13, False),
    (14, "إبراهيم",  "Abraham",                  "Abraham",               52,  13, True),
    (15, "الحجر",    "Al-Hijr",                  "The Rocky Tract",       99,  14, True),
    (16, "النحل",    "Les Abeilles",             "The Bee",               128, 14, True),
    (17, "الإسراء",  "Le Voyage Nocturne",       "The Night Journey",     111, 15, True),
    (18, "الكهف",    "La Caverne",               "The Cave",              110, 15, True),
    (19, "مريم",     "Marie",                    "Mary",                  98,  16, True),
    (20, "طه",       "Tâ-Hâ",                   "Ta-Ha",                 135, 16, True),
    (21, "الأنبياء", "Les Prophètes",            "The Prophets",          112, 17, True),
    (22, "الحج",     "Le Pèlerinage",            "The Pilgrimage",        78,  17, False),
    (23, "المؤمنون", "Les Croyants",             "The Believers",         118, 18, True),
    (24, "النور",    "La Lumière",               "The Light",             64,  18, False),
    (25, "الفرقان",  "Le Discernement",          "The Criterion",         77,  18, True),
    (26, "الشعراء",  "Les Poètes",              "The Poets",             227, 19, True),
    (27, "النمل",    "Les Fourmis",              "The Ant",               93,  19, True),
    (28, "القصص",    "Les Récits",              "The Stories",           88,  20, True),
    (29, "العنكبوت", "L'Araignée",               "The Spider",            69,  20, True),
    (30, "الروم",    "Les Byzantins",            "The Romans",            60,  21, True),
    (31, "لقمان",    "Luqmân",                   "Luqman",                34,  21, True),
    (32, "السجدة",   "La Prosternation",         "The Prostration",       30,  21, True),
    (33, "الأحزاب",  "Les Coalisés",             "The Combined Forces",   73,  21, False),
    (34, "سبأ",      "Sabâ",                     "Sheba",                 54,  22, True),
    (35, "فاطر",     "Le Créateur",              "Originator",            45,  22, True),
    (36, "يس",       "Yâ-Sîn",                  "Ya Sin",                83,  22, True),
    (37, "الصافات",  "Les Rangées",              "Those who set the Ranks", 182, 23, True),
    (38, "ص",        "Sâd",                      "The Letter Sad",        88,  23, True),
    (39, "الزمر",    "Les Groupes",              "The Troops",            75,  23, True),
    (40, "غافر",     "Le Pardonneur",            "The Forgiver",          85,  24, True),
    (41, "فصلت",     "Exposées",                 "Explained in Detail",   54,  24, True),
    (42, "الشورى",   "La Consultation",          "The Consultation",      53,  25, True),
    (43, "الزخرف",   "Les Ornements",            "The Gold Adornments",   89,  25, True),
    (44, "الدخان",   "La Fumée",                 "The Smoke",             59,  25, True),
    (45, "الجاثية",  "L'Agenouillée",            "The Crouching",         37,  25, True),
    (46, "الأحقاف",  "Les Dunes",               "The Wind-Curved Sandhills", 35, 26, True),
    (47, "محمد",     "Mohammed",                 "Muhammad",              38,  26, False),
    (48, "الفتح",    "La Victoire",              "The Victory",           29,  26, False),
    (49, "الحجرات",  "Les Appartements",         "The Rooms",             18,  26, False),
    (50, "ق",        "Qâf",                      "The Letter Qaf",        45,  26, True),
    (51, "الذاريات", "Les Dispersantes",         "The Winnowing Winds",   60,  26, True),
    (52, "الطور",    "Le Mont Sinaï",            "The Mount",             49,  27, True),
    (53, "النجم",    "L'Étoile",                 "The Star",              62,  27, True),
    (54, "القمر",    "La Lune",                  "The Moon",              55,  27, True),
    (55, "الرحمن",   "Le Tout Miséricordieux",   "The Beneficent",        78,  27, False),
    (56, "الواقعة",  "L'Événement",              "The Inevitable",        96,  27, True),
    (57, "الحديد",   "Le Fer",                   "The Iron",              29,  27, False),
    (58, "المجادلة", "La Discussion",            "The Pleading Woman",    22,  28, False),
    (59, "الحشر",    "L'Exode",                  "The Exile",             24,  28, False),
    (60, "الممتحنة", "L'Éprouvée",               "She that is to be Examined", 13, 28, False),
    (61, "الصف",     "Le Rang",                  "The Ranks",             14,  28, False),
    (62, "الجمعة",   "Le Vendredi",              "The Congregation",      11,  28, False),
    (63, "المنافقون","Les Hypocrites",            "The Hypocrites",        11,  28, False),
    (64, "التغابن",  "La Tricherie",             "The Mutual Disillusion", 18, 28, False),
    (65, "الطلاق",   "Le Divorce",               "The Divorce",           12,  28, False),
    (66, "التحريم",  "L'Interdiction",           "The Prohibition",       12,  28, False),
    (67, "الملك",    "La Royauté",               "The Sovereignty",       30,  29, True),
    (68, "القلم",    "La Plume",                 "The Pen",               52,  29, True),
    (69, "الحاقة",   "L'Inévitable",             "The Reality",           52,  29, True),
    (70, "المعارج",  "Les Voies d'Ascension",    "The Ascending Stairways", 44, 29, True),
    (71, "نوح",      "Noé",                      "Noah",                  28,  29, True),
    (72, "الجن",     "Les Djinns",               "The Jinn",              28,  29, True),
    (73, "المزمل",   "L'Enveloppé",              "The Enshrouded One",    20,  29, True),
    (74, "المدثر",   "Le Revêtu",                "The Cloaked One",       56,  29, True),
    (75, "القيامة",  "La Résurrection",          "The Resurrection",      40,  29, True),
    (76, "الإنسان",  "L'Homme",                  "The Man",               31,  29, False),
    (77, "المرسلات", "Les Envoyés",              "The Emissaries",        50,  29, True),
    (78, "النبأ",    "La Nouvelle",              "The Tidings",           40,  30, True),
    (79, "النازعات", "Les Arracheurs",           "Those who Drag Forth",  46,  30, True),
    (80, "عبس",      "Il a froncé",              "He Frowned",            42,  30, True),
    (81, "التكوير",  "L'Enroulement",            "The Overthrowing",      29,  30, True),
    (82, "الانفطار", "La Déchirure",             "The Cleaving",          19,  30, True),
    (83, "المطففين", "Les Fraudeurs",            "The Defrauding",        36,  30, True),
    (84, "الانشقاق", "La Fente",                 "The Sundering",         25,  30, True),
    (85, "البروج",   "Les Constellations",       "The Mansions of the Stars", 22, 30, True),
    (86, "الطارق",   "L'Astre Nocturne",         "The Nightcommer",       17,  30, True),
    (87, "الأعلى",   "Le Très-Haut",             "The Most High",         19,  30, True),
    (88, "الغاشية",  "L'Enveloppante",           "The Overwhelming",      26,  30, True),
    (89, "الفجر",    "L'Aube",                   "The Dawn",              30,  30, True),
    (90, "البلد",    "La Cité",                  "The City",              20,  30, True),
    (91, "الشمس",    "Le Soleil",                "The Sun",               15,  30, True),
    (92, "الليل",    "La Nuit",                  "The Night",             21,  30, True),
    (93, "الضحى",    "La Matinée",               "The Morning Hours",     11,  30, True),
    (94, "الشرح",    "L'Expansion",              "The Relief",            8,   30, True),
    (95, "التين",    "Le Figuier",               "The Fig",               8,   30, True),
    (96, "العلق",    "Le Caillot",               "The Clot",              19,  30, True),
    (97, "القدر",    "La Destinée",              "The Power",             5,   30, True),
    (98, "البينة",   "La Preuve",                "The Clear Proof",       8,   30, False),
    (99, "الزلزلة",  "Le Séisme",                "The Earthquake",        8,   30, False),
    (100,"العاديات", "Les Coureurs",             "The Courser",           11,  30, True),
    (101,"القارعة",  "Le Fracas",                "The Calamity",          11,  30, True),
    (102,"التكاثر",  "L'Accumulation",           "The Rivalry in World Increase", 8, 30, True),
    (103,"العصر",    "L'Époque",                 "The Declining Day",     3,   30, True),
    (104,"الهمزة",   "Le Calomniateur",          "The Traducer",          9,   30, True),
    (105,"الفيل",    "L'Éléphant",               "The Elephant",          5,   30, True),
    (106,"قريش",     "Quraych",                  "Quraysh",               4,   30, True),
    (107,"الماعون",  "L'Aide Courante",          "The Small Kindnesses",  7,   30, True),
    (108,"الكوثر",   "L'Abondance",              "The Abundance",         3,   30, True),
    (109,"الكافرون", "Les Infidèles",            "The Disbelievers",      6,   30, True),
    (110,"النصر",    "Le Secours",               "The Divine Support",    3,   30, False),
    (111,"المسد",    "Les Fibres",               "The Palm Fiber",        5,   30, True),
    (112,"الإخلاص",  "Le Monothéisme Pur",       "Sincerity",             4,   30, True),
    (113,"الفلق",    "L'Aube Naissante",         "The Daybreak",          5,   30, True),
    (114,"الناس",    "Les Hommes",               "Mankind",               6,   30, True),
]


def seed_surahs(db=None) -> None:
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        existing = db.query(Surah).count()
        if existing >= 114:
            print("Surahs already seeded.")
            return

        for row in SURAHS_DATA:
            num, ar, fr, en, verses, juz, meccan = row
            if db.get(Surah, num):
                continue
            db.add(Surah(
                surah_number=num,
                surah_name_ar=ar,
                surah_name_fr=fr,
                surah_name_en=en,
                total_verses=verses,
                juz_number=juz,
                is_meccan=meccan,
            ))

        db.commit()
        print(f"Seeded {len(SURAHS_DATA)} surahs.")
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    seed_surahs()
