import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    print("WARNING: GOOGLE_API_KEY is not set correctly in .env")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI(title="RAG Company Policy Chatbot")

# Setup directories for static files and templates
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

DB_DIR = "./chroma_db"

# Initialize HuggingFace Embeddings for local document embedding
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # Initialize Chroma Vector Store (Read-only for the API)
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    print("Chroma DB successfully loaded.")
except Exception as e:
    print(f"Warning: Could not load vectorstore (did you run ingest.py?): {e}")
    vectorstore = None

class ChatRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the frontend chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Retrieve relevant document chunks and generate a response using Gemini."""
    if not vectorstore:
        return {
            "answer": "The knowledge base is currently unavailable. Please contact the administrator.",
            "sources": []
        }
        
    try:
        # Retrieve top 3 relevant chunks
        results = vectorstore.similarity_search(request.question, k=3)
        
        if not results:
            return {
                "answer": "I could not find this information in the company documents.",
                "sources": []
            }

        context = "\n\n".join([f"Document: {doc.metadata.get('source', 'Unknown')} (Page {doc.metadata.get('page', 'Unknown')})\n{doc.page_content}" for doc in results])
        
        # Prepare prompt for Gemini
        prompt = f"""
You are a helpful company policy assistant.
Answer the user's question ONLY using the retrieved context below.
If you cannot find the answer in the provided context, you must reply EXACTLY with:
"I could not find this information in the company documents."

Context:
{context}

Question: {request.question}
"""
        
        # Generate response using Google Generative AI
        response = model.generate_content(prompt)
        
        # Extract unique sources
        sources = list(set([doc.metadata.get("source", "Unknown") for doc in results]))
        
        return {
            "answer": response.text,
            "sources": sources
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sources": []}