from langchain_google_genai import ChatGoogleGenerativeAI
from modder_mc_service.util.llm_init import load_env,   LoadEnvResponse
import os 
resp: LoadEnvResponse = load_env()
assert resp.LEVEL < 2, resp.MSG
def get_google_ai(tools: list) -> ChatGoogleGenerativeAI:
    """Initializes and returns a Google Gemini LLM instance.

    Returns:
        ChatGoogleGenerativeAI: The initialized Google Gemini LLM instance.
    """
    key = os.getenv("GEMINI_API_KEY")
    assert key is not None, "GEMINI_API_KEY environment variable is required"
    google_ai = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=key)
    google_ai = google_ai.bind_tools(tools)
    return google_ai