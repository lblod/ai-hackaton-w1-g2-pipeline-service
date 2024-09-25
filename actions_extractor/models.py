from enum import Enum
from typing import List, Optional

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class PossibleActionCategories(Enum):
    DAK_BUITENMUUR_DAKBEDEKKING_GOOT="DAK_BUITENMUUR_DAKBEDEKKING_GOOT"
    DAK_BUITENMUUR_AFWERKINGSLAAG_KLEUR="DAK_BUITENMUUR_AFWERKINGSLAAG_KLEUR"
    DAK_BUITENMUUR_AFWERKINGSLAAG_TEXTUUR="DAK_BUITENMUUR_AFWERKINGSLAAG_TEXTUUR"
    DAK_BUITENMUUR_BUITENSCHRIJNWERK="DAK_BUITENMUUR_BUITENSCHRIJNWERK"
    DAK_BUITENMUUR_VASTE_ELEMENTEN="DAK_BUITENMUUR_VASTE_ELEMENTEN"
    TUIN_PARK_BEGRAAFPLAATS="TUIN_PARK_BEGRAAFPLAATS"
    INTERIEUR_ARCHITECTUUR="INTERIEUR_ARCHITECTUUR"
    INTERIEUR_DECORATIE="INTERIEUR_DECORATIE"


class Action(BaseModel):
    """"Information about the extracted action"""
    action: Optional[str] = Field(description="The complete text of an action")
    permit_needed: Optional[bool] = Field(description="Is a permit needed for this action", default=True)
    category: Optional[str] = Field(description="Category the action belongs to")


class Actions(BaseModel):
    allowed_action_list: Optional[List[Action]]
    not_allowed_action_list: Optional[List[Action]]


output_parser= PydanticOutputParser(pydantic_object=Actions)
