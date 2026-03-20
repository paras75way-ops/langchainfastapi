import os
import json
import uuid
from datetime import datetime
from fastapi import UploadFile

 
UPLOAD_DIR = "uploads"
REGISTRY_FILE = "pdfs.json"


 

def load_registry() -> dict:
    """Read pdfs.json and return its contents as a dict.
    If the file doesn't exist yet, return an empty registry."""
    if not os.path.exists(REGISTRY_FILE):
        return {"pdfs": {}}
    with open(REGISTRY_FILE, "r") as f:
        return json.load(f)


def save_registry(registry: dict):
    """Write the registry dict back to pdfs.json"""
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)


 

async def save_pdf(file: UploadFile) -> dict:
    """
    Save an uploaded PDF to disk and register it in pdfs.json.

    Steps:
    1. Generate a unique ID for this PDF
    2. Save the file to /uploads folder
    3. Add an entry to pdfs.json
    4. Return the pdf info
    """

     
    pdf_id = str(uuid.uuid4())[:8]

 
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, f"{pdf_id}.pdf")
 
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    
    registry = load_registry()
    registry["pdfs"][pdf_id] = {
        "pdf_id": pdf_id,
        "filename": file.filename,        
        "file_path": file_path,           
        "uploaded_at": datetime.now().isoformat()
    }
    save_registry(registry)

 
    return registry["pdfs"][pdf_id]


def list_pdfs() -> list:
    """
    Return all uploaded PDFs from the registry.
    """
    registry = load_registry()
    return list(registry["pdfs"].values())


def delete_pdf(pdf_id: str) -> dict:
    """
    Delete a PDF from disk and remove it from the registry.

    Steps:
    1. Check if pdf_id exists in registry
    2. Delete the file from /uploads
    3. Remove the entry from pdfs.json
    4. Return the deleted pdf info
    """

    # Step 1: Check if it exists
    registry = load_registry()
    if pdf_id not in registry["pdfs"]:
        return None   # caller will handle 404

    pdf_info = registry["pdfs"][pdf_id]

 
    file_path = pdf_info["file_path"]
    if os.path.exists(file_path):
        os.remove(file_path)

  
    del registry["pdfs"][pdf_id]
    save_registry(registry)

    # Step 4: Return deleted info so caller knows what was deleted
    return pdf_info


def get_pdf(pdf_id: str) -> dict:
    """
    Get a single PDF's info by its ID.
    Returns None if not found.
    """
    registry = load_registry()
    return registry["pdfs"].get(pdf_id, None)