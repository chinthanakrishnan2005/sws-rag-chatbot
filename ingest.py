import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DOCS_DIR = "./docs"
DB_DIR = "./chroma_db"

def ingest_documents():
    os.makedirs(DOCS_DIR, exist_ok=True)
    
    # Get all PDF files in the docs directory
    pdf_files = glob.glob(os.path.join(DOCS_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {DOCS_DIR}. Please add some and try again.")
        return

    print(f"Found {len(pdf_files)} PDF(s). Starting ingestion...")
    
    all_documents = []
    
    # Load each PDF
    for file_path in pdf_files:
        print(f"Loading {file_path}...")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        # Ensure metadata has source
        for doc in documents:
            doc.metadata['source'] = os.path.basename(file_path)
        all_documents.extend(documents)
        
    print(f"Total pages loaded: {len(all_documents)}")
    
    # Split text
    # The requirement is chunk_size = 500, chunk_overlap = 50
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"Split into {len(chunks)} chunks.")
    
    # Embeddings
    print("Initializing embeddings (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Store in ChromaDB
    print("Creating vector database...")
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_DIR
    )
    vectorstore.persist()
    print(f"Successfully ingested and saved to {DB_DIR}!")

if __name__ == "__main__":
    ingest_documents()
