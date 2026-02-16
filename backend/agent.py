# rag_agent_app/backend/agent.py

import os
from typing import List, Literal, TypedDict
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

# Import API keys from config
from config import GROQ_API_KEY, TAVILY_API_KEY
from vectorstore import get_retriever

# --- Tools ---
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
