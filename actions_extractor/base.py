from abc import ABC, abstractmethod

from actions_extractor.models import ActionFragment
from typing import Optional, List

class ActionsExtractor(ABC):
    @abstractmethod
    def extract_actions(self, text: str) -> List[ActionFragment]:
        pass
