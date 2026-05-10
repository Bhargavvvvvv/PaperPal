from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

class LLMService:
    def __init__(self, config):
        self.config = config

    def get_embeddings(self):
        if self.config.LLM_TYPE == "openai":
            # Requires: pip install langchain-openai
            from langchain_openai import OpenAIEmbeddings
            return OpenAIEmbeddings(api_key=self.config.OPENAI_API_KEY)
        return HuggingFaceEmbeddings()

    def get_llm(self):
        if self.config.LLM_TYPE == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                api_key=self.config.OPENAI_API_KEY, 
                model="gpt-4"
            )
            
        return ChatOllama(model=self.config.LOCAL_MODEL_NAME)

    def get_vectorstore(self, text_chunks):
        embeddings = self.get_embeddings()
        return FAISS.from_texts(texts=text_chunks, embedding=embeddings)