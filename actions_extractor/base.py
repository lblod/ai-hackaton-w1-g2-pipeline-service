from abc import ABC, abstractmethod

from actions_extractor.models import ActionFragment


class ActionsExtractor(ABC):
    @abstractmethod
    def extract_actions(self, text: str) -> list[ActionFragment]:
        pass
