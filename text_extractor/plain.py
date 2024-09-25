from io import BytesIO

from pypdf import PdfReader

from text_extractor.base import TextExtractor

class PlainTextExtractor(TextExtractor):
    def extract_text(self, buffer: BytesIO) -> str:
        reader = PdfReader(buffer)
        text = ""
        for page in reader.pages:
            text_page = page.extract_text()
            text += text_page + "\n"
        return text
