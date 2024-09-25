from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field


class ActionCategory(StrEnum):
    DAK_BUITENMUUR_DAKBEDEKKING_GOOT = "DAK_BUITENMUUR_DAKBEDEKKING_GOOT"
    DAK_BUITENMUUR_AFWERKINGSLAAG_KLEUR = "DAK_BUITENMUUR_AFWERKINGSLAAG_KLEUR"
    DAK_BUITENMUUR_AFWERKINGSLAAG_TEXTUUR = "DAK_BUITENMUUR_AFWERKINGSLAAG_TEXTUUR"
    DAK_BUITENMUUR_BUITENSCHRIJNWERK = "DAK_BUITENMUUR_BUITENSCHRIJNWERK"
    DAK_BUITENMUUR_VASTE_ELEMENTEN = "DAK_BUITENMUUR_VASTE_ELEMENTEN"
    TUIN_PARK_BEGRAAFPLAATS = "TUIN_PARK_BEGRAAFPLAATS"
    INTERIEUR_ARCHITECTUUR = "INTERIEUR_ARCHITECTUUR"
    INTERIEUR_DECORATIE = "INTERIEUR_DECORATIE"


class MeasureType(StrEnum):
    NEEDS_PERMIT = "NeedsPermit"
    FORBIDDEN = "Forbidden"
    ALLOWED_WITHOUT_PERMIT = "AllowedWithoutPermit"


class Action(BaseModel):
    """"Information about the extracted action"""
    action: Optional[str] = Field(description="The complete text of an action")
    forbidden: Optional[bool] = Field(description="Is the action forbidden on the heritage property", default=False)
    permit_needed: Optional[bool] = Field(description="Is a permit needed for this action", default=True)
    category: Optional[str] = Field(description="Category the action belongs to")


class Actions(BaseModel):
    allowed_action_list: list[Action] = []
    not_allowed_action_list: list[Action] = []


class ActionFragment(BaseModel):
    text_fragment: str
    measure_type: MeasureType
    category: ActionCategory | None
