from pydantic import BaseModel
from typing import List
from datetime import datetime


class ChatRequest(BaseModel):
    """What the user sends when asking a question"""
    question: str        
 
 
class SourceInfo(BaseModel):
    """Info about which part of which PDF the answer came from"""
    filename: str        
    page: int            
 
 
class ChatResponse(BaseModel):
    """What we return after answering the question"""
    question: str        # echo back the original question
    answer: str          # the LLM generated answer
    sources: List[SourceInfo]  # which PDFs/pages were used
 