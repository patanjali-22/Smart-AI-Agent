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

from config import GROQ_API_KEY, TAVILY_API_KEY
from vectorstore import get_retriever

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
tavily = TavilySearch(max_results=3, topic="general")

@tool
def web_search_tool(query: str) -> str:
    """Up-to-date web info via Tavily"""
    try:
        result = tavily.invoke({"query": query})
        if isinstance(result, dict) and 'results' in result:
            formatted_results = []
            for item in result['results']:
                title = item.get('title', 'No title')
                content = item.get('content', 'No content')
                url = item.get('url', '')
                formatted_results.append(f"Title: {title}\nContent: {content}\nURL: {url}")
            return "\n\n".join(formatted_results) if formatted_results else "No results found"
        else:
            return str(result)
    except Exception as e:
        return f"WEB_ERROR::{e}"

@tool
def rag_search_tool(query: str) -> str:
    """Top-K chunks from KB (empty string if none)"""
    try:
        retriever_instance = get_retriever()
        docs = retriever_instance.invoke(query, k=5)
        return "\n\n".join(d.page_content for d in docs) if docs else ""
    except Exception as e:
        return f"RAG_ERROR::{e}"

# --- Pydantic schemas for structured output ---
class RouteDecision(BaseModel):
    route: Literal["rag", "web", "answer", "end"]
    reply: str | None = Field(None, description="Filled only when route == 'end'")

class RagJudge(BaseModel):
    sufficient: bool = Field(..., description="True if retrieved information is sufficient to answer the user's question, False otherwise.")

# --- LLM instances with structured output where needed ---
router_llm = ChatGroq(model="llama3-70b-8192", temperature=0).with_structured_output(RouteDecision)
judge_llm = ChatGroq(model="llama3-70b-8192", temperature=0).with_structured_output(RagJudge)
answer_llm = ChatGroq(model="llama3-70b-8192", temperature=0.7)

# --- Shared state type ---
class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    route: Literal["rag", "web", "answer", "end"]
    rag: str
    web: str
    web_search_enabled: bool
