from io import BytesIO
from pypdf import PdfReader


def extract_text(bytes_buffer: BytesIO):
    reader = PdfReader(bytes_buffer)
    text = ""
    for page in reader.pages:
        text_page = page.extract_text()
        text += text_page + "\n"
    return text
