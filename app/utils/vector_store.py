import os
import shutil
import logging
from typing import List, Optional
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Vector store management with ChromaDB"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Ensure directory exists
        os.makedirs(db_path, exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """Create vector store from documents"""
        try:
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.db_path
            )
            vectorstore.persist()
            
            logger.info(f"Created vector store with {len(documents)} documents")
            return vectorstore
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            raise
    
    def load_vectorstore(self) -> Optional[Chroma]:
        """Load existing vector store"""
        try:
            if os.path.exists(self.db_path) and os.listdir(self.db_path):
                vectorstore = Chroma(
                    persist_directory=self.db_path,
                    embedding_function=self.embeddings
                )
                return vectorstore
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
        
        return None
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """Perform similarity search"""
        vectorstore = self.load_vectorstore()
        if vectorstore:
            return vectorstore.similarity_search(query, k=k)
        return []
    
    def get_document_count(self) -> int:
        """Get number of documents in vector store"""
        vectorstore = self.load_vectorstore()
        if vectorstore:
            try:
                return vectorstore._collection.count()
            except:
                return 0
        return 0
    
    def clear_database(self):
        """Clear the vector database"""
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)
            os.makedirs(self.db_path, exist_ok=True)
            logger.info("Vector database cleared")