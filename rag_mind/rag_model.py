import os
from typing import List, Dict
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from huggingface_hub import InferenceClient
from pypdf import PdfReader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)
from .utils import word_wrap


class RAGModel:
    """
    Retrieval-Augmented Generation model using ChromaDB and Hugging Face.
    """
    
    def __init__(self, hf_api_key: str, collection_name: str = "rag_collection"):
        """
        Initialize the RAG model.
        
        Args:
            hf_api_key (str): Hugging Face API key
            collection_name (str): Name for the ChromaDB collection
        """
        self.hf_api_key = hf_api_key
        self.collection_name = collection_name
        
        # Initialize embedding function
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="BAAI/bge-small-en"
        )
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        # Initialize text splitters
        self.character_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=1000,
            chunk_overlap=100
        )
        
        self.token_splitter = SentenceTransformersTokenTextSplitter(
            chunk_overlap=50,
            tokens_per_chunk=256
        )
        
        # Initialize Hugging Face client
        self.hf_model = "mistralai/Mistral-7B-Instruct-v0.2"
    
    def load_documents_from_directory(self, directory_path: str) -> List[Dict]:
        """
        Load both PDF and text files from a directory.
        
        Args:
            directory_path (str): Path to the directory containing documents
            
        Returns:
            list: List of document dictionaries with 'id' and 'text' keys
        """
        print(f"==== Loading documents from {directory_path} ====")
        documents = []
        
        if not os.path.exists(directory_path):
            print(f"Warning: Directory {directory_path} does not exist")
            return documents
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Handle text files
            if filename.endswith(".txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        text = file.read().strip()
                        if text:
                            documents.append({"id": filename, "text": text})
                            print(f"  ✓ Loaded text file: {filename}")
                except Exception as e:
                    print(f"  ✗ Error loading {filename}: {e}")
            
            # Handle PDF files
            elif filename.endswith(".pdf"):
                try:
                    reader = PdfReader(file_path)
                    pdf_texts = [p.extract_text().strip() for p in reader.pages]
                    pdf_texts = [text for text in pdf_texts if text]
                    
                    if pdf_texts:
                        combined_text = "\n\n".join(pdf_texts)
                        documents.append({
                            "id": filename,
                            "text": combined_text
                        })
                        print(f"  ✓ Loaded PDF: {filename} ({len(pdf_texts)} pages)")
                except Exception as e:
                    print(f"  ✗ Error loading {filename}: {e}")
        
        print(f"\nTotal documents loaded: {len(documents)}")
        return documents
    
    def process_and_index_documents(self, directory_paths: List[str]):
        """
        Process documents from multiple directories and index them in ChromaDB.
        
        Args:
            directory_paths (list): List of directory paths containing documents
        """
        all_documents = []
        
        # Load documents from all directories
        for directory_path in directory_paths:
            docs = self.load_documents_from_directory(directory_path)
            all_documents.extend(docs)
        
        if not all_documents:
            print("No documents to process")
            return
        
        # Combine all text
        combined_text = "\n\n".join([doc["text"] for doc in all_documents])
        
        # Split text with character splitter
        print("==== Splitting text with RecursiveCharacterTextSplitter ====")
        character_split_texts = self.character_splitter.split_text(combined_text)
        print(f"Character chunks: {len(character_split_texts)}")
        
        # Further split with token splitter
        print("==== Further splitting with SentenceTransformersTokenTextSplitter ====")
        token_split_texts = []
        for text in character_split_texts:
            token_split_texts += self.token_splitter.split_text(text)
        
        print(f"Total token-based chunks: {len(token_split_texts)}")
        
        # Index in ChromaDB
        print("==== Inserting chunks into ChromaDB ====")
        ids = [str(i) for i in range(len(token_split_texts))]
        self.collection.upsert(
            ids=ids,
            documents=token_split_texts
        )
        
        print(f"✓ Indexed {self.collection.count()} chunks in ChromaDB")
    
    def augment_query(self, query: str) -> str:
        """
        Augment query with hypothetical answer for better retrieval.
        
        Args:
            query (str): Original query
            
        Returns:
            str: Augmented query
        """
        prompt = """You are a helpful expert research assistant. 
        Provide an example answer to the given question, that might be found in a document.
        Keep it brief and factual."""
        
        client = InferenceClient(model=self.hf_model, token=self.hf_api_key)
        
        try:
            response = client.chat_completion(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query}
                ],
                max_tokens=150
            )
            hypothetical_answer = response.choices[0].message.content
            return f"{query} {hypothetical_answer}"
        except Exception as e:
            print(f"Warning: Query augmentation failed: {e}")
            return query
    
    def query_documents(self, question: str, n_results: int = 5, use_augmentation: bool = True) -> List[str]:
        """
        Query documents and retrieve relevant chunks.
        
        Args:
            question (str): User's question
            n_results (int): Number of results to retrieve
            use_augmentation (bool): Whether to use query augmentation
            
        Returns:
            list: List of relevant document chunks
        """
        if use_augmentation:
            query_text = self.augment_query(question)
        else:
            query_text = question
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["documents"]
        )
        
        relevant_chunks = results["documents"][0] if results["documents"] else []
        return relevant_chunks
    
    def generate_response(self, question: str, relevant_chunks: List[str]) -> str:
        """
        Generate response using Hugging Face Inference API.
        
        Args:
            question (str): User's question
            relevant_chunks (list): Retrieved document chunks
            
        Returns:
            str: Generated answer
        """
        if not relevant_chunks:
            return "I couldn't find relevant information to answer your question."
        
        context = "\n\n".join([f"[Context {i+1}]\n{chunk}" for i, chunk in enumerate(relevant_chunks)])
        
        prompt = f"""You are a helpful assistant. Use the following context to answer the question accurately and concisely.

Context:
{context}

Question: {question}

Instructions:
- Answer based on the context provided
- Be specific and cite relevant details
- If the context doesn't contain enough information, say so
- Keep the answer clear and concise

Answer:"""

        client = InferenceClient(model=self.hf_model, token=self.hf_api_key)
        
        try:
            response = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def answer_question(self, question: str, n_results: int = 5, use_augmentation: bool = True) -> Dict:
        """
        Complete RAG pipeline: retrieve relevant documents and generate answer.
        
        Args:
            question (str): User's question
            n_results (int): Number of document chunks to retrieve
            use_augmentation (bool): Whether to use query augmentation
            
        Returns:
            dict: Dictionary containing answer and retrieved chunks
        """
        relevant_chunks = self.query_documents(question, n_results, use_augmentation)
        answer = self.generate_response(question, relevant_chunks)
        
        return {
            "answer": answer,
            "relevant_chunks": relevant_chunks,
            "num_chunks": len(relevant_chunks)
        }
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the current collection.
        
        Returns:
            dict: Collection statistics
        """
        return {
            "collection_name": self.collection_name,
            "total_chunks": self.collection.count()
        }
    
    def clear_collection(self):
        """
        Clear all documents from the collection.
        """
        # Delete the collection
        self.chroma_client.delete_collection(name=self.collection_name)
        
        # Recreate it
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        print(f"✓ Collection '{self.collection_name}' cleared")
