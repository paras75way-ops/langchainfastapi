import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.chat import ChatRequest, ChatResponse, SourceInfo
from app.services.vector_service import query_vectorstore

load_dotenv()

router = APIRouter()

# ───────────────────────────────────────────
# Gemini LLM setup
# We use gemini-1.5-flash — fast and free tier available
# ───────────────────────────────────────────

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3   # lower = more factual, less creative
)


# ───────────────────────────────────────────
# POST /chat/ask
# ───────────────────────────────────────────

@router.post("/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest):
    """
    Answer a question using only the uploaded PDFs as context.

    Steps:
    1. Search Chroma for relevant chunks
    2. If no chunks found, tell user to upload PDFs
    3. Build a prompt with chunks as context
    4. Call Gemini LLM
    5. Return answer + sources
    """

    # Step 1: Find relevant chunks from Chroma
    # This embeds the question and finds top 4 similar chunks
    chunks = query_vectorstore(request.question, k=4)

    # Step 2: If no PDFs uploaded yet, return early
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No documents found. Please upload PDF files first."
        )

    # Step 3: Build context string from chunks
    # We combine all chunk texts into one big context block
    # Each chunk also tells us which file and page it came from
    context = ""
    for i, chunk in enumerate(chunks):
        filename = chunk.metadata.get("filename", "unknown")
        page = chunk.metadata.get("page", 0)
        context += f"\n--- Chunk {i+1} (from: {filename}, page: {page+1}) ---\n"
        context += chunk.page_content
        context += "\n"

    # Step 4: Build the prompt
    # System message tells LLM to ONLY use the provided context
    # This is what keeps answers grounded in your PDFs only
    system_prompt = """You are a helpful assistant that answers questions 
strictly based on the provided document context.

Rules:
- Only use information from the context below to answer
- If the answer is not in the context, say "I could not find this information in the uploaded documents"
- Be concise and accurate
- Mention which document the answer came from"""

    user_prompt = f"""Context from uploaded documents:
{context}

Question: {request.question}

Answer:"""

    # Step 5: Call Gemini LLM with the prompt
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    answer = response.content

    # Step 6: Build sources list from chunk metadata
    # Deduplicate — same file+page shouldn't appear twice
    seen = set()
    sources = []
    for chunk in chunks:
        filename = chunk.metadata.get("filename", "unknown")
        page = chunk.metadata.get("page", 0)
        key = (filename, page)
        if key not in seen:
            seen.add(key)
            sources.append(SourceInfo(
                filename=filename,
                page=page + 1   # convert 0-indexed to 1-indexed
            ))

    # Step 7: Return the full response
    return ChatResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )