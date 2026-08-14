import fitz  # PyMuPDF
from PIL import Image
from typing import List

def pdf_to_images(pdf_bytes: bytes) -> List[Image.Image]:
    """Converts every page of a PDF document into a list of PIL Images."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render at 200 DPI for high resolution QA/QC check
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
        
    return images
