"""
Quran reference data endpoints.

Routes:
  GET /quran/surahs            — all 114 surahs
  GET /quran/surahs/{number}   — single surah
"""
from fastapi import APIRouter, HTTPException
from ..core.dependencies import CurrentUser, DB
from ..models.quran import Surah
from ..schemas.task import SurahOut

router = APIRouter(prefix="/quran", tags=["Quran"])


@router.get("/surahs", response_model=list[SurahOut])
def list_surahs(current_user: CurrentUser, db: DB):
    return db.query(Surah).order_by(Surah.surah_number).all()


@router.get("/surahs/{surah_number}", response_model=SurahOut)
def get_surah(surah_number: int, current_user: CurrentUser, db: DB):
    surah = db.query(Surah).filter(Surah.surah_number == surah_number).first()
    if not surah:
        raise HTTPException(status_code=404, detail="Sourate introuvable")
    return surah
