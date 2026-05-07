# 📄 PaperPal

PaperPal is an accessible, AI-powered research assistant designed to help you interact with complex PDFs using local AI models. By running completely on your own hardware, it ensures absolute privacy for your documents while featuring cognitive accessibility tools tailored for neurodivergent and dyslexic thinkers.

## ✨ Features

* **🧠 Dyslexia Focus Mode:** A built-in accessibility toggle that instantly switches the UI to the OpenDyslexic font, increases letter spacing, and applies a low-glare, warm color palette to reduce visual fatigue.
* **100% Local Processing:** Keeps your research completely private by using local LLMs for generation and embeddings.
* **Smart Contextual Q&A:** Ask questions about dense academic papers and get clear, easy-to-read answers backed by local vector search.
* **Accessible Output:** AI responses are formatted with markdown (bullet points, bold text) and optimized prompts ensure the LLM focuses on your core intent.

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/Bhargavvvvvv/PaperPal.git
cd PaperPal
```

### Setting up the Local AI Backend (Ollama)

For this application to work offline and privately, you need a local LLM runner. We recommend Ollama.

Download and install Ollama.

Open your terminal and pull the necessary models:
```bash
ollama run llama3.1
ollama pull nomic-embed-text
```
### Setting up the Python Backend (Flask)
Open a new terminal window and navigate to your backend folder:

```bash
pip install -r requirements.txt
python app.py
```

(Ensure your requirements.txt includes flask, flask-cors, langchain, PyPDF2, and faiss-cpu)

### Setting up the Frontend (Next.js)
Open a third terminal window and navigate to your frontend folder:

```bash
npm install
npm run dev
```
## 📄 Supported Formats
Currently, PaperPal supports PDFs. The extraction works best on natively exported PDFs where text is selectable. If you are processing scanned or older papers, we highly recommend pre-processing them with OCRmyPDF to add a readable text layer before uploading.

## 🤝 Contributing
Contributions are welcome! Whether you want to add support for a new local AI backend, improve the PDF chunking strategy, or add more neurodivergent accessibility features to the UI, please consider opening an issue before submitting a pull request to discuss the proposed changes.

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
