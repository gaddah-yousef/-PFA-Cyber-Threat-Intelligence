from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser
from app.services.reflex_sheets import REFLEX_SHEETS

router = APIRouter(prefix="/api/reflex-sheets", tags=["Fiches réflexes"])


@router.get("")
def list_reflex_sheets(_current_user: CurrentUser) -> dict[str, dict[str, object]]:
    return REFLEX_SHEETS


@router.get("/{threat_type}")
def get_reflex_sheet(threat_type: str, _current_user: CurrentUser) -> dict[str, object]:
    sheet = REFLEX_SHEETS.get(threat_type)
    if not sheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fiche réflexe introuvable",
        )
    return {"threat_type": threat_type, **sheet}
