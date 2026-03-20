from pydantic import BaseModel
from typing import List
from datetime import datetime
 
 
 
class PDFUploadResponse(BaseModel):
    """Returned after a PDF is successfully uploaded"""
    pdf_id: str           
    filename: str         
    message: str          
 
 
class PDFListItem(BaseModel):
    """One item in the list of uploaded PDFs"""
    pdf_id: str
    filename: str
    uploaded_at: str      
 
class PDFListResponse(BaseModel):
    """Returned when user asks for all uploaded PDFs"""
    pdfs: List[PDFListItem]
    total: int           
 
 
class PDFDeleteResponse(BaseModel):
    """Returned after a PDF is deleted"""
    pdf_id: str
    message: str          
 
 