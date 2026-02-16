# rag_agent_app/backend/main.py

import os
import time
from typing import List, Dict, Any
import tempfile

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.document_loaders import PyPDFLoader



from agent import rag_agent
from vectorstore import add_document_to_vectorstore

# Initialize FastAPI app
app = FastAPI(
    title="LangGraph RAG Agent API",
    description="API for the LangGraph-powered RAG agent with Pinecone and Groq.",
    version="1.0.0",
)

# In-memory session manager for LangGraph checkpoints (for demonstration)
memory = MemorySaver()

# --- Pydantic Models for API ---
class TraceEvent(BaseModel):
    step: int
    node_name: str
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)
    event_type: str

class QueryRequest(BaseModel):
    session_id: str
    query: str
    enable_web_search: bool = True # NEW: Add web search toggle state

class AgentResponse(BaseModel):
    response: str
    trace_events: List[TraceEvent] = Field(default_factory=list)

class DocumentUploadResponse(BaseModel):
    message: str
    filename: str
    processed_chunks: int
