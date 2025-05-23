import logging
import streamlit as st
from typing import Dict, List, Optional
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class ModelManager:
    """Model management with installation and removal capabilities"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.recommended_models = {
            "llama3.1:8b": {
                "description": "Meta's Llama 3.1 8B - Great balance of performance and speed",
                "size": "4.7GB",
                "use_case": "General Q&A, reasoning"
            },
            "llama3.1:70b": {
                "description": "Meta's Llama 3.1 70B - Highest quality responses",
                "size": "40GB",
                "use_case": "Complex reasoning, professional use"
            },
            "codellama:7b": {
                "description": "Code-focused model for programming tasks",
                "size": "3.8GB",
                "use_case": "Code generation, debugging"
            },
            "mistral:7b": {
                "description": "Mistral 7B - Fast and efficient",
                "size": "4.1GB",
                "use_case": "Quick responses, general tasks"
            },
            "phi3:mini": {
                "description": "Microsoft Phi-3 Mini - Compact but capable",
                "size": "2.3GB",
                "use_case": "Resource-constrained environments"
            }
        }
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed model information"""
        return self.ollama_client.get_model_info(model_name)
    
    def install_model(self, model_name: str) -> bool:
        """Install model with progress tracking"""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(data):
            if "total" in data and "completed" in data:
                progress = data["completed"] / data["total"]
                progress_bar.progress(progress)
                status_text.text(f"Downloading: {progress:.1%}")
            elif "status" in data:
                status_text.text(f"Status: {data['status']}")
        
        success = self.ollama_client.pull_model(model_name, progress_callback)
        
        if success:
            progress_bar.progress(1.0)
            status_text.text("✅ Installation complete!")
        
        return success
    
    def remove_model(self, model_name: str) -> bool:
        """Remove model"""
        return self.ollama_client.remove_model(model_name)
    
    def get_recommended_models(self) -> Dict:
        """Get list of recommended models"""
        return self.recommended_models