from .user import User, TeacherStudentLink
from .program import Program
from .task import Task, TaskCompletion
from .streak import Streak, JokerUsage
from .notification import Notification
from .quran import Surah
from .curriculum import (
    CurriculumProgram, CurriculumUnit, CurriculumItem,
    StudentEnrollment, StudentItemProgress, StudentSubmission,
)
from .autonomous_learning import (
    QuranWord, ArabicRoot, QuranChunk,
    StudentModuleProgress, LeitnerCard,
    ExerciseSession, ExerciseAttempt,
)
from .hifz_master import (
    HifzGoal, VerseProgress, HifzSession,
    StudentXP, StudentBadge,
    VerseMastery, GoalMode, BadgeType, StudentLevel,
)
from .diagnostic import (
    DiagnosticQuestion, DiagnosticSession, DiagnosticResult,
)
from .flashcard import (
    FlashcardCard, FlashcardProgress,
)
from .gamification import (
    XPEvent, Badge, MedineBadgeUnlock,
)
from .medine_v2 import MedineV2Progress

__all__ = [
    "User", "TeacherStudentLink",
    "Program",
    "Task", "TaskCompletion",
    "Streak", "JokerUsage",
    "Notification",
    "Surah",
    "CurriculumProgram", "CurriculumUnit", "CurriculumItem",
    "StudentEnrollment", "StudentItemProgress", "StudentSubmission",
    "QuranWord", "ArabicRoot", "QuranChunk",
    "StudentModuleProgress", "LeitnerCard",
    "ExerciseSession", "ExerciseAttempt",
    "HifzGoal", "VerseProgress", "HifzSession",
    "StudentXP", "StudentBadge",
    "VerseMastery", "GoalMode", "BadgeType", "StudentLevel",
    "DiagnosticQuestion", "DiagnosticSession", "DiagnosticResult",
    "FlashcardCard", "FlashcardProgress",
    "XPEvent", "Badge", "MedineBadgeUnlock",
    "MedineV2Progress",
]
