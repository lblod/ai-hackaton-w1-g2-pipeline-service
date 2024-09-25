from abc import ABC, abstractmethod
from io import BytesIO

class TextExtractor(ABC):
    @abstractmethod
    def extract_text(buffer: BytesIO) -> str:
        pass