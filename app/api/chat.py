import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app.models.chat import ChatRequest, ChatResponse, SourceInfo
from app.services.vector_service import query_vectorstore
 
load_dotenv()

router = APIRouter()
 
 
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
 
)

 

@router.post("/ask", response_model=ChatResponse)
def ask_question(request: ChatRequest):
    """
    Answer a question using only the uploaded PDFs as context.

    Steps:
    1. Search Chroma for relevant chunks
    2. If no chunks found, tell user to upload PDFs
    3. Build a prompt with chunks as context
    4. Call grok LLM
    5. Return answer + sources
    """

    
    chunks = query_vectorstore(request.question, k=4)
 
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No documents found. Please upload PDF files first."
        )

   
    context = ""
    for i, chunk in enumerate(chunks):
        filename = chunk.metadata.get("filename", "unknown")
        page = chunk.metadata.get("page", 0)
        context += f"\n--- Chunk {i+1} (from: {filename}, page: {page+1}) ---\n"
        context += chunk.page_content
        context += "\n"

    system_prompt = """You are a helpful AI assistant.

You MUST answer using ONLY the provided context.

Instructions:
- If the answer is present in the context, you MUST answer it.
- Do NOT say "not found" if the answer exists even partially.
- Only say "I could not find this information in the uploaded documents" if the answer is completely missing.
- Be precise and use the exact information from context.
- Always include supporting details from the context."""

    user_prompt = f"""Context from uploaded documents:
{context}

Question: {request.question}

Answer:"""

    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]

    response = llm.invoke(messages)
    answer = response.content

    
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
                page=page + 1   
            ))


    return ChatResponse(
        question=request.question,
        answer=answer,
        sources=sources
    )