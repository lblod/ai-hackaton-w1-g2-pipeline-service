from abc import ABC, abstractmethod

from actions_extractor.models import Actions


class ActionsExtractor(ABC):
    @abstractmethod
    def extract_actions(self, text: str) -> Actions:
        pass
