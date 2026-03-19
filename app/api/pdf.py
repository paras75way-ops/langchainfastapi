from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.pdf import PDFUploadResponse, PDFListResponse, PDFListItem, PDFDeleteResponse
from app.services.pdf_service import save_pdf, list_pdfs, delete_pdf
from app.services.vector_service import add_to_vectorstore, delete_from_vectorstore

router = APIRouter()


# ───────────────────────────────────────────
# POST /pdf/upload
# ───────────────────────────────────────────

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF file.

    Steps:
    1. Validate it's actually a PDF
    2. Save file to disk via pdf_service
    3. Chunk + embed + store in Chroma via vector_service
    4. Return pdf_id and filename
    """

    # Step 1: Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Step 2: Save file to disk and register in pdfs.json
    pdf_info = await save_pdf(file)

    # Step 3: Chunk, embed and store in Chroma
    # This is the heavy step — calls Gemini API to embed chunks
    add_to_vectorstore(
        pdf_id=pdf_info["pdf_id"],
        file_path=pdf_info["file_path"],
        filename=pdf_info["filename"]
    )

    # Step 4: Return response
    return PDFUploadResponse(
        pdf_id=pdf_info["pdf_id"],
        filename=pdf_info["filename"],
        message=f"'{pdf_info['filename']}' uploaded and indexed successfully"
    )


# ───────────────────────────────────────────
# GET /pdf/list
# ───────────────────────────────────────────

@router.get("/list", response_model=PDFListResponse)
def get_all_pdfs():
    """
    Return a list of all uploaded PDFs.
    Reads from pdfs.json registry.
    """

    pdfs = list_pdfs()

    # Convert raw dicts to PDFListItem Pydantic models
    pdf_items = [
        PDFListItem(
            pdf_id=p["pdf_id"],
            filename=p["filename"],
            uploaded_at=p["uploaded_at"]
        )
        for p in pdfs
    ]

    return PDFListResponse(
        pdfs=pdf_items,
        total=len(pdf_items)
    )


# ───────────────────────────────────────────
# DELETE /pdf/{pdf_id}
# ───────────────────────────────────────────

@router.delete("/{pdf_id}", response_model=PDFDeleteResponse)
def remove_pdf(pdf_id: str):
    """
    Delete a PDF by its ID.

    Steps:
    1. Delete vectors from Chroma
    2. Delete file from disk + remove from pdfs.json
    3. Return confirmation
    """

    # Step 1: Remove all chunks from Chroma first
    # (we do this before deleting the registry entry)
    delete_from_vectorstore(pdf_id)

    # Step 2: Delete file from disk and registry
    deleted = delete_pdf(pdf_id)

    # If pdf_id not found in registry, return 404
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"PDF with id '{pdf_id}' not found"
        )

    # Step 3: Return confirmation
    return PDFDeleteResponse(
        pdf_id=pdf_id,
        message=f"'{deleted['filename']}' deleted successfully"
    )