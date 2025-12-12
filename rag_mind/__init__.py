"""
RAG Mind - Retrieval-Augmented Generation Package

This package contains the core RAG model and utilities for document processing,
embeddings, and question answering.
"""

from .rag_model import RAGModel
from .config import ConfigManager
from .utils import word_wrap, project_embeddings

__all__ = ['RAGModel', 'ConfigManager', 'word_wrap', 'project_embeddings']
__version__ = '1.0.0'
