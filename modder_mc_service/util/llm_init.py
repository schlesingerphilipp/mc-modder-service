import os
from typing import Tuple
from pydantic import BaseModel

def load_env_from_file() -> Tuple[bool, bool]:
    # load the file .llm_env if it exists
    if os.path.exists(".llm_env"):
        with open(".llm_env") as f:
            for line in f:
                key, value = line.split("=")
                os.environ[key] = value.strip()
        required_key = os.getenv("LANGCHAIN_API_KEY")
        return True, required_key is not None
    return False, False

class LoadEnvResponse(BaseModel):
    MSG: str
    LEVEL: int


def load_env() -> LoadEnvResponse:  
    loaded, required_are_present = load_env_from_file()
    if loaded:
        return LoadEnvResponse(MSG="Environment variables loaded from .llm_env file.", LEVEL=0)
    else:
        return LoadEnvResponse(MSG="Only .llm_env file is supported for loading environment variables.", LEVEL=2)