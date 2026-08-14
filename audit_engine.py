from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field
from typing import List

class DrawingIssue(BaseModel):
    issue_type: str = Field(description="e.g., Missing Dimension, Wrong Finish, Setting-Out Mismatch")
    tag_id: str = Field(description="Member or part mark ID referenced, e.g., B-101")
    description: str = Field(description="Detailed explanation of the error found.")
    severity: str = Field(description="High, Medium, or Low")

class AuditReport(BaseModel):
    passed: bool
    issues: List[DrawingIssue]

def run_drawing_audit(fab_drawing: Image.Image, setting_out_drawing: Image.Image, api_key: str) -> AuditReport:
    # Explicitly specify api_version to ensure compatibility
    client = genai.Client(api_key=api_key)
    
    prompt = """
    You are a Senior Structural & Architectural Quality Control Auditor.
    Analyze the provided Fabrication Drawing (Image 1) and Setting-Out / Tagging Drawing (Image 2).
    
    Perform these specific checks:
    1. Check for any MISSING DIMENSIONS required for manufacturing (overall length, hole centers, flange thickness, etc.).
    2. Check for FINISH MISMATCHES (e.g., callout says Galvanized on setting-out but Painted/Mill Finish on fab drawing).
    3. Check SETTING-OUT MISMATCHES (compare member lengths, grid references, and tag IDs between both drawings).
    
    Return a structured list of all identified issues.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[prompt, fab_drawing, setting_out_drawing],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AuditReport,
            temperature=0.1
        )
    )
    return AuditReport.model_validate_json(response.text)