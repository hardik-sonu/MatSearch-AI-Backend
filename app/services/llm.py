
import os

from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from backend/.env
load_dotenv()


def get_llm() -> BaseChatModel:
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()

    if provider != "gemini":
        raise ValueError(
            f"Unsupported LLM_PROVIDER: {provider}. "
            "MatSearch AI is configured to use Gemini."
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Check the backend .env file."
        )

    model_name = os.getenv(
        "LLM_MODEL",
        "gemini-3.8-flash",
    ).strip()

    if not model_name:
        raise ValueError("LLM_MODEL is empty.")

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0,
    )
