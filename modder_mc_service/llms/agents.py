from langchain_google_genai import ChatGoogleGenerativeAI
import os 

def get_google_ai() -> ChatGoogleGenerativeAI:
    """Initializes and returns a Google Gemini LLM instance.

    Returns:
        ChatGoogleGenerativeAI: The initialized Google Gemini LLM instance.
    """
    key = os.getenv("GEMINI_API_KEY")
    assert key is not None, "GEMINI_API_KEY environment variable is required"
    google_ai = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=key)
    return google_ai