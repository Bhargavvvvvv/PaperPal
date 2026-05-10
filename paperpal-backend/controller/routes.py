from flask import Blueprint, request, jsonify
from config.config import Config
from services.document_service import DocumentService
from services.llm_service import LLMService
from services.chat_service import ChatService

api_bp = Blueprint('api', __name__)

# Initialize singletons for local app scope
config = Config()
document_service = DocumentService(config.DATA_DIR, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
llm_service = LLMService(config)
chat_service = ChatService(llm_service)

@api_bp.route('/process-document', methods=['POST'])
def process_document():
    file = request.files.get('file')
    essay_text = request.form.get('essay_text', '')

    if not file:
        return jsonify({"error": "No file provided"}), 400
        
    try:
        raw_text = document_service.process_pdf(file)
        text_chunks = document_service.get_text_chunks(raw_text)
        vectorstore = llm_service.get_vectorstore(text_chunks)
        
        chat_service.initialize_chain(vectorstore)
        
        ai_prompt = essay_text if essay_text else "Please provide a clear, easy-to-understand summary of this document."
        chat_service.process_message(ai_prompt)

        return jsonify({
            "status": "success",
            "message": "Document processed and ready for chat.",
            "chat_history": chat_service.get_formatted_history()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('question')

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        chat_service.process_message(user_question)
        return jsonify({
            "status": "success",
            "chat_history": chat_service.get_formatted_history()
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500