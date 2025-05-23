"""
RAG System Components Module

This module contains all the core components for the RAG system:
- DocumentProcessor: Advanced document processing with OCR
- OllamaClient: LLM client for inference
- ModelManager: Model installation and management
- ChatInterface: Interactive chat functionality
- SystemMonitor: System monitoring and health checks
"""

__version__ = "1.0.0"
__author__ = "RAG System Team"

# Import all components for easy access
from .document_processor import DocumentProcessor
from .ollama_client import OllamaClient
from .model_manager import ModelManager
from .chat_interface import ChatInterface
from .monitoring import SystemMonitor

__all__ = [
    'DocumentProcessor',
    'OllamaClient', 
    'ModelManager',
    'ChatInterface',
    'SystemMonitor'
]