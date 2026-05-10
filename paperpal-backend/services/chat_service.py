from langchain_classic.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ConversationBufferMemory
from langchain.messages import HumanMessage, AIMessage

CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template("""
You are an expert science communicator and cognitive accessibility specialist. Your goal is to answer the user's question by translating dense academic text into highly readable, accessible language for neurodivergent and dyslexic readers.

You will be provided with specific extracted sections of a research paper (Context) and a question (User Question). 

### STRICT ACCESSIBILITY RULES:
1. Cognitive Load Reduction: Keep sentences short and punchy. Limit paragraphs to a maximum of 3 sentences. Never output a "wall of text."
2. Plain Language: Remove all academic jargon. If a complex concept is crucial to the answer, explain it immediately using everyday analogies.
3. Visual Hierarchy: Use bullet points or numbered lists to break down multi-step concepts.
4. Typography: Use **bolding** for key terms to help the eye track. NEVER use italics.

### STRICT RAG GROUNDING RULES:
1. You must base your answer EXCLUSIVELY on the provided Context chunks. 
2. Do not include outside knowledge or make assumptions.
3. If the Context chunks do not contain the information needed to answer the question, you must respond exactly with: "The provided sections of the paper do not contain the answer to this question."

=== EXTRACTED CONTEXT ===
{chat_history}
========================

You are a helpful, clear, and concise assistant. The following prompt is from a user who may have dyslexia or neurodivergent thinking patterns. Please focus entirely on the core intent and meaning of their message, disregarding any spelling, grammar, or structural irregularities.

When replying:
Use plain, straightforward language.
Break your response into short paragraphs or use bullet points.
Avoid overly complex jargon unless specifically asked.
Do not correct the user's spelling or grammar.
               
USER QUESTION: {question}

ACCESSIBLE ANSWER:        
""")

class ChatService:
    def __init__(self, llm_service):
        self.llm_service = llm_service
        self.conversation_chain = None
        self.chat_history = []

    def initialize_chain(self, vectorstore):
        model = self.llm_service.get_llm()
        vc = vectorstore.as_retriever(search_kwargs={"k": 8})
        
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=model,
            retriever=vc,
            memory=memory,
            condense_question_prompt=CONDENSE_QUESTION_PROMPT
        )
        self.chat_history = []

    def process_message(self, question: str):
        if not self.conversation_chain:
            raise ValueError("Please upload a document first.")
            
        response = self.conversation_chain.invoke({
            'question': question,
            'chat_history': self.chat_history
        })
        self.chat_history = response.get('chat_history', [])
        return self.chat_history

    def get_formatted_history(self):
        formatted_messages = []
        for message in self.chat_history:
            if isinstance(message, HumanMessage):
                formatted_messages.append({"role": "human", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_messages.append({"role": "ai", "content": message.content})
        return formatted_messages