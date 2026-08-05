import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(provided_key: str = None) -> str:
    """Retrieve Groq API key from explicit user input, session state, or environment variables."""
    if provided_key and provided_key.strip():
        return provided_key.strip()
    return os.getenv("GROQ_API_KEY", "")

def get_llm(
    api_key: str = None,
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.7
):
    """Instantiate LangChain ChatGroq model."""
    key = get_api_key(api_key)
    if not key:
        raise ValueError("Groq API Key is missing. Please enter your key in the sidebar or set GROQ_API_KEY in .env")

    from langchain_groq import ChatGroq
    effective_model = model_name if model_name else "llama-3.3-70b-versatile"
    return ChatGroq(
        model_name=effective_model,
        groq_api_key=key,
        temperature=temperature
    )
