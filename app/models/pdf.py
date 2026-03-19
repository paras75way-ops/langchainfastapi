from pydantic import BaseModel
from typing import List
from datetime import datetime
 
 
 
class PDFUploadResponse(BaseModel):
    """Returned after a PDF is successfully uploaded"""
    pdf_id: str          # unique ID we generate for this PDF
    filename: str        # original filename e.g. "document.pdf"
    message: str         # e.g. "PDF uploaded and indexed successfully"
 
 
class PDFListItem(BaseModel):
    """One item in the list of uploaded PDFs"""
    pdf_id: str
    filename: str
    uploaded_at: str     # ISO format datetime string e.g. "2024-01-15T10:30:00"
 
 
class PDFListResponse(BaseModel):
    """Returned when user asks for all uploaded PDFs"""
    pdfs: List[PDFListItem]
    total: int           # total count of PDFs
 
 
class PDFDeleteResponse(BaseModel):
    """Returned after a PDF is deleted"""
    pdf_id: str
    message: str         # e.g. "PDF deleted successfully"
 
 