import os
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentService:
    def __init__(self, data_dir: str, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.data_dir = data_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def process_pdf(self, pdf_file) -> str:
        text = ""
        filename = os.path.join(self.data_dir, pdf_file.filename)
        pdf_reader = PdfReader(pdf_file)
        
        for page in pdf_reader.pages:
            text += page.extract_text()
            
        with open(filename, "w", encoding="utf-8") as op_file:
            op_file.write(text)
            
        return text

    def get_text_chunks(self, text: str):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, 
            chunk_overlap=self.chunk_overlap
        )
        return text_splitter.split_text(text)