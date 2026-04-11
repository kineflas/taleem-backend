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
]
