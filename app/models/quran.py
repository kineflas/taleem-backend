from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Surah(Base):
    __tablename__ = "surahs"

    surah_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    surah_name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    surah_name_fr: Mapped[str] = mapped_column(String(100), nullable=False)
    surah_name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    total_verses: Mapped[int] = mapped_column(Integer, nullable=False)
    juz_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_meccan: Mapped[bool] = mapped_column(Boolean, default=True)
