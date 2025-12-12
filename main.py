from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from rag_mind.rag_model import RAGModel
from rag_mind.config import ConfigManager

import uvicorn

# Load environment variables
load_dotenv()

# Get Hugging Face API key
hf_api_key = os.getenv("HF_API_KEY")
if not hf_api_key:
    raise ValueError("HF_API_KEY not found in .env file")

# Initialize FastAPI app
app = FastAPI(title="RAG Question Answering System", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize config manager and RAG model
config_manager = ConfigManager()
rag_model = None


def initialize_rag_model():
    """Initialize or reinitialize the RAG model with current config."""
    global rag_model
    collection_name = config_manager.get_setting("collection_name", "rag_collection")
    rag_model = RAGModel(hf_api_key=hf_api_key, collection_name=collection_name)
    
    # Load and index documents from configured paths
    document_paths = config_manager.get_document_paths()
    if document_paths:
        try:
            rag_model.process_and_index_documents(document_paths)
        except Exception as e:
            print(f"Warning: Error indexing documents: {e}")


# Initialize on startup
initialize_rag_model()


# Pydantic models for request/response
class QuestionRequest(BaseModel):
    question: str
    n_results: Optional[int] = 5
    use_augmentation: Optional[bool] = True


class QuestionResponse(BaseModel):
    answer: str
    relevant_chunks: List[str]
    num_chunks: int


class DocumentPathRequest(BaseModel):
    path: str


class SettingsUpdate(BaseModel):
    document_paths: Optional[List[str]] = None
    n_results: Optional[int] = None
    use_augmentation: Optional[bool] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    tokens_per_chunk: Optional[int] = None


# API Endpoints

@app.get("/")
async def read_root():
    """Serve the main HTML page."""
    return FileResponse("static/index.html")


@app.post("/api/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a question using the RAG model.
    """
    if not rag_model:
        raise HTTPException(status_code=500, detail="RAG model not initialized")
    
    try:
        result = rag_model.answer_question(
            question=request.question,
            n_results=request.n_results,
            use_augmentation=request.use_augmentation
        )
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/settings")
async def get_settings():
    """
    Get all configuration settings.
    """
    return config_manager.get_all_settings()


@app.post("/api/settings")
async def update_settings(settings: SettingsUpdate):
    """
    Update configuration settings.
    """
    try:
        # Update each provided setting
        if settings.document_paths is not None:
            config_manager.update_setting("document_paths", settings.document_paths)
        if settings.n_results is not None:
            config_manager.update_setting("n_results", settings.n_results)
        if settings.use_augmentation is not None:
            config_manager.update_setting("use_augmentation", settings.use_augmentation)
        if settings.chunk_size is not None:
            config_manager.update_setting("chunk_size", settings.chunk_size)
        if settings.chunk_overlap is not None:
            config_manager.update_setting("chunk_overlap", settings.chunk_overlap)
        if settings.tokens_per_chunk is not None:
            config_manager.update_setting("tokens_per_chunk", settings.tokens_per_chunk)
        
        return {"message": "Settings updated successfully", "settings": config_manager.get_all_settings()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document-path/add")
async def add_document_path(request: DocumentPathRequest):
    """
    Add a new document path.
    """
    try:
        success = config_manager.add_document_path(request.path)
        if success:
            return {"message": f"Document path '{request.path}' added successfully"}
        else:
            return {"message": f"Document path '{request.path}' already exists"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/document-path/remove")
async def remove_document_path(request: DocumentPathRequest):
    """
    Remove a document path.
    """
    try:
        success = config_manager.remove_document_path(request.path)
        if success:
            return {"message": f"Document path '{request.path}' removed successfully"}
        else:
            return {"message": f"Document path '{request.path}' not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reindex")
async def reindex_documents():
    """
    Reindex all documents from configured paths.
    """
    try:
        # Clear existing collection
        rag_model.clear_collection()
        
        # Reindex documents
        document_paths = config_manager.get_document_paths()
        rag_model.process_and_index_documents(document_paths)
        
        stats = rag_model.get_collection_stats()
        return {"message": "Documents reindexed successfully", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """
    Get collection statistics.
    """
    if not rag_model:
        raise HTTPException(status_code=500, detail="RAG model not initialized")
    
    try:
        stats = rag_model.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)