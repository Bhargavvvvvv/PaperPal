import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_TYPE = os.getenv("LLM_TYPE", "local")
    LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "llama3.1")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    DATA_DIR = os.getenv("DATA_DIR", "__data__")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]