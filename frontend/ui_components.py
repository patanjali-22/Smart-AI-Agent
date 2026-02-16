# rag_agent_app/frontend/ui_components.py

import streamlit as st
from backend_api import upload_document_to_backend, chat_with_backend_agent
from session_manager import init_session_state # Import to access session state

def display_header():
    """Renders the main title and introductory markdown."""
    st.set_page_config(page_title="AI Agent Chatbot", layout="wide") # Set page config here
    st.title("🤖 AI Agent Chatbot")
    st.markdown("Ask me anything! I can answer questions using my internal knowledge (RAG) or by searching the web.")
    st.markdown("---")

def render_document_upload_section(fastapi_base_url: str):
    """
    Renders the UI for uploading PDF documents to the knowledge base.
    Handles file upload and API call to the backend.
    """
    st.header("Upload Document to Knowledge Base")
    with st.expander("Upload New Document (PDF Only)"):
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="pdf_uploader")
        
        if st.button("Upload PDF", key="upload_pdf_button"):
            if uploaded_file is not None:
                with st.spinner(f"Uploading {uploaded_file.name}..."):
                    try:
                        upload_data = upload_document_to_backend(fastapi_base_url, uploaded_file)
                        st.success(f"PDF '{upload_data.get('filename')}' uploaded successfully! Processed {upload_data.get('processed_chunks')} pages.")
                    except Exception as e:
                        st.error(f"An error occurred during upload: {e}")
            else:
                st.warning("Please upload a PDF file before clicking 'Upload PDF'.")
    st.markdown("---")
