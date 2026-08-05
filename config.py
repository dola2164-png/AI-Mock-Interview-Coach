import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_api_key(provided_key: str = None) -> str:
    """Retrieve Groq API key from user input, Streamlit Cloud secrets, or environment variables."""
    if provided_key and provided_key.strip():
        return provided_key.strip()
    
    # Check Streamlit Secrets (for Streamlit Community Cloud Deployment)
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            key = st.secrets["GROQ_API_KEY"]
            if key and key.strip():
                return key.strip()
    except Exception:
        pass
        
    # Check Environment Variable (.env)
    return os.getenv("GROQ_API_KEY", "")

def get_llm(
    api_key: str = None,
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7
):
    """Instantiate LangChain ChatGroq model."""
    key = get_api_key(api_key)
    if not key:
        raise ValueError("Groq API Key is missing. Please enter your key in the sidebar, set GROQ_API_KEY in .env, or configure Streamlit Secrets.")

    from langchain_groq import ChatGroq
    effective_model = model_name if model_name else "llama-3.3-70b-versatile"
    return ChatGroq(
        model_name=effective_model,
        groq_api_key=key,
        temperature=temperature
    )
