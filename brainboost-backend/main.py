import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
from PyPDF2 import PdfReader
from langchain_classic.memory import ConversationBufferMemory

from flask_cors import CORS

from flask import Flask,request,jsonify
DATA_DIR = "__data__"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["OPTIONS", "GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}, supports_credentials=True)

vectorstore = None
conversation_chain = None
chat_history = []
# @app.route('/')
# def home():
#     return render_template('index.html')
global_conversation_chain = None
chat_history = []



from langchain.messages import HumanMessage, AIMessage

def format_chat_history(langchain_history):
    formatted_messages = []
    
    for message in langchain_history:
        if isinstance(message, HumanMessage):
            formatted_messages.append({
                "role": "human", 
                "content": message.content
            })
        elif isinstance(message, AIMessage):
            formatted_messages.append({
                "role": "ai", 
                "content": message.content
            })
            
    return formatted_messages
def get_pdf_text(pdf):
    text = ""
    pdf_txt = ""
    filename = os.path.join(DATA_DIR,pdf.filename)
    pdf_reader = PdfReader(pdf)
    for page in pdf_reader.pages:
        text += page.extract_text()
        pdf_txt += page.extract_text()
    with (open(filename, "w", encoding="utf-8")) as op_file:
        op_file.write(pdf_txt)
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)
    return chunks



def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings()
    db = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return db


def get_conversation_chain(vectorstore):
    model=ChatOllama(model="llama3.1")    
    vc = vectorstore.as_retriever(search_kwargs={"k": 8})
    print(f"vectorstore == >> {vectorstore}")
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
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=vc,
        memory=memory,
        condense_question_prompt=CONDENSE_QUESTION_PROMPT
    )

    return conversation_chain


@app.route('/api/process-document', methods=['POST'])
def process_document():
    global global_conversation_chain, chat_history

    file = request.files.get('file')
    essay_text = request.form.get('essay_text', '')

    if not file:
        return jsonify({"error": "No file provided"}), 400
    raw_text = get_pdf_text(file)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)
    global_conversation_chain = get_conversation_chain(vectorstore)
    

    chat_history = [] 

    if essay_text == "":
        ai_prompt = "Please provide a clear, easy-to-understand summary of this document."
    else:
        ai_prompt = essay_text

    response = global_conversation_chain.invoke({
        'question': ai_prompt,
        'chat_history': chat_history
    })
    print(response)
    chat_history = response.get('chat_history', [])

    return jsonify({
        "status": "success",
        "message": "Document processed and ready for chat.",
        "chat_history": format_chat_history(chat_history)
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    print("lets checkk")
    global global_conversation_chain, chat_history

    # Only rely on the JSON data coming from React
    data = request.get_json()
    user_question = data.get('question')
    print(f"NEW CHAT: {user_question}")

    if not global_conversation_chain:
        return jsonify({"error": "Please upload a document first."}), 400

    if global_conversation_chain is not None and user_question:
        response = global_conversation_chain.invoke({
            'question': f"""{user_question}""",
            'chat_history': chat_history
        })
        chat_history = response.get('chat_history', []) 

    clean_history = format_chat_history(chat_history)

    return jsonify({
        "status": "success",
        "chat_history": clean_history # Already formatted!
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)