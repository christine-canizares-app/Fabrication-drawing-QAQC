from google import genai
from google.genai import types
from PIL import Image, ImageDraw
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple

class DrawingIssue(BaseModel):
    issue_type: str = Field(description="e.g., Missing Dimension, Wrong Finish, Setting-Out Mismatch")
    tag_id: str = Field(description="Member or part mark ID referenced, e.g., B-101")
    description: str = Field(description="Detailed explanation of the error found.")
    severity: str = Field(description="High, Medium, or Low")
    box_2d: Optional[List[int]] = Field(
        default=None, 
        description="Bounding box of error location on Fabrication Drawing formatted as [ymin, xmin, ymax, xmax] (0-1000 scale)."
    )

class AuditReport(BaseModel):
    passed: bool
    issues: List[DrawingIssue]

def highlight_errors(image: Image.Image, issues: List[DrawingIssue]) -> Image.Image:
    """Overlays red bounding boxes and issue tags directly on the drawing image."""
    annotated_img = image.copy().convert("RGBA")
    overlay = Image.new("RGBA", annotated_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = annotated_img.size

    for idx, issue in enumerate(issues, start=1):
        if issue.box_2d and len(issue.box_2d) == 4:
            ymin, xmin, ymax, xmax = issue.box_2d
            
            abs_ymin = int((ymin / 1000.0) * height)
            abs_xmin = int((xmin / 1000.0) * width)
            abs_ymax = int((ymax / 1000.0) * height)
            abs_xmax = int((xmax / 1000.0) * width)

            draw.rectangle(
                [(abs_xmin, abs_ymin), (abs_xmax, abs_ymax)],
                fill=(255, 0, 0, 45),
                outline=(255, 0, 0, 255),
                width=4
            )
            
            label_text = f"#{idx}: {issue.tag_id}"
            draw.rectangle(
                [(abs_xmin, max(0, abs_ymin - 25)), (abs_xmin + 130, abs_ymin)],
                fill=(255, 0, 0, 220)
            )
            draw.text((abs_xmin + 5, max(0, abs_ymin - 20)), label_text, fill=(255, 255, 255, 255))

    return Image.alpha_composite(annotated_img, overlay).convert("RGB")

def audit_single_page(
    fab_page: Image.Image, 
    setting_out_images: List[Image.Image], 
    api_key: str, 
    page_num: int
) -> Tuple[AuditReport, Image.Image]:
    """Audits one fabrication drawing page against all setting-out reference pages."""
    clean_key = api_key.strip()
    client = genai.Client(api_key=clean_key)
    
    prompt = f"""
    You are a Senior Structural & Architectural Quality Control Auditor.
    You are evaluating Page {page_num} of a multi-page Fabrication Drawing set (Image 1) against the provided Setting-Out / Tagging Plan(s).
    
    Perform these specific checks:
    1. Check for MISSING DIMENSIONS required for manufacturing.
    2. Check for FINISH MISMATCHES between drawings.
    3. Check SETTING-OUT MISMATCHES (compare member lengths, grid references, and tag IDs).
    
    CRITICAL: For every issue identified on Page {page_num} of the Fabrication Drawing (Image 1), provide exact `box_2d` bounding box coordinates [ymin, xmin, ymax, xmax] normalized from 0 to 1000 pinpointing where the error occurs.
    """
    
    contents = [prompt, fab_page] + setting_out_images
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AuditReport,
            temperature=0.1
        )
    )
    
    report = AuditReport.model_validate_json(response.text)
    annotated_fab = highlight_errors(fab_page, report.issues)
    
    return report, annotated_fab
