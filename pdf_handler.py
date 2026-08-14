import fitz  # PyMuPDF
from PIL import Image
import io

def pdf_page_to_image(pdf_bytes: bytes, page_num: int = 0, dpi: int = 300) -> Image.Image:
    """Converts a specific PDF page to a high-res PIL Image."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_num)
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img_data = pix.tobytes("png")
    return Image.open(io.BytesIO(img_data))