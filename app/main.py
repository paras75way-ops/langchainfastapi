from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import pdf, chat

# ───────────────────────────────────────────
# Create FastAPI app
# ───────────────────────────────────────────

app = FastAPI(
    title="RAG API",
    description="Upload PDFs and ask questions — answers come only from your documents",
    version="1.0.0"
)

# ───────────────────────────────────────────
# CORS Middleware
# Allows frontend (browser) to talk to this API
# In production replace "*" with your actual frontend URL
# ───────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────────────────────────────────────
# Register Routers
# Each router handles a group of related endpoints
# ───────────────────────────────────────────

app.include_router(pdf.router, prefix="/pdf", tags=["PDF"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


# ───────────────────────────────────────────
# Health Check
# ───────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "message": "RAG API is up!"}