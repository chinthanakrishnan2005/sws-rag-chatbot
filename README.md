# SWS RAG Chatbot

A complete Retrieval-Augmented Generation (RAG) chatbot using FastAPI, LangChain, ChromaDB, HuggingFace Embeddings, and the Gemini API.

## Architecture

1. **Frontend**: A modern responsive white & blue UI utilizing HTML, CSS, and vanilla JavaScript.
2. **Backend**: FastAPI serving the frontend and the `/api/chat` endpoint.
3. **Ingestion**: A standalone script (`ingest.py`) parses PDFs using LangChain and stores their embeddings in a Chroma vector database.
4. **Retrieval**: Uses HuggingFace `all-MiniLM-L6-v2` embeddings for fast and accurate local semantic search.
5. **Generation**: Uses the `gemini-1.5-flash` model to answer user questions strictly based on the retrieved context.

## Setup Instructions

1. **Install Dependencies**
   Make sure you are using your virtual environment, then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   Open the `.env` file and set your Google API key:
   ```env
   GOOGLE_API_KEY=your_actual_api_key
   ```

3. **Ingest Documents**
   Place your company policy PDF documents into the `docs/` folder.
   Run the ingestion script to create the vector database:
   ```bash
   python ingest.py
   ```

4. **Run the Server**
   Start the FastAPI server:
   ```bash
   uvicorn app:app --reload
   ```

5. **Chat**
   Open your browser and navigate to: `http://127.0.0.1:8000`
