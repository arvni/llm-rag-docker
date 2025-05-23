import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any
import streamlit as st

logger = logging.getLogger(__name__)

class OllamaClient:
    """Enhanced Ollama client with advanced features"""
    
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 120
        
    def is_healthy(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def wait_for_ollama(self, timeout: int = 60) -> bool:
        """Wait for Ollama to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_healthy():
                return True
            time.sleep(2)
        return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return []
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed model information"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
        return None
    
    def pull_model(self, model_name: str, progress_callback=None) -> bool:
        """Pull a model with progress tracking"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if progress_callback:
                                progress_callback(data)
                            
                            # Check if pull is complete
                            if data.get("status") == "success":
                                return True
                                
                        except json.JSONDecodeError:
                            continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
    
    def remove_model(self, model_name: str) -> bool:
        """Remove a model"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/delete",
                json={"name": model_name}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error removing model {model_name}: {e}")
            return False
    
    def generate(self, model: str, prompt: str, context: str = "", 
                stream: bool = False, **kwargs) -> str:
        """Generate response from Ollama"""
        
        # Build the full prompt
        if context:
            full_prompt = self._build_rag_prompt(prompt, context)
        else:
            full_prompt = prompt
        
        # Default generation parameters
        options = {
            "temperature": kwargs.get("temperature", 0.1),
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 40),
            "num_predict": kwargs.get("max_tokens", 1000),
            "stop": kwargs.get("stop", [])
        }
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": stream,
            "options": options
        }
        
        try:
            if stream:
                return self._generate_stream(payload)
            else:
                return self._generate_single(payload)
                
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def _generate_single(self, payload: Dict) -> str:
        """Generate single response"""
        response = self.session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def _generate_stream(self, payload: Dict):
        """Generate streaming response"""
        response = self.session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=True
        )
        
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if not data.get("done", False):
                            yield data.get("response", "")
                    except json.JSONDecodeError:
                        continue
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    def _build_rag_prompt(self, question: str, context: str) -> str:
        """Build RAG-optimized prompt"""
        return f"""You are a helpful AI assistant that answers questions based on provided context.

Context Information:
{context}

Instructions:
- Answer the question based ONLY on the provided context
- If the answer is not in the context, say "I cannot find this information in the provided documents"
- Be concise but comprehensive
- Use specific quotes from the context when possible
- Maintain a helpful and professional tone

Question: {question}

Answer:"""
    
    def chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Chat interface for conversation"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "top_k": kwargs.get("top_k", 40)
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"Error in chat: {str(e)}"
    
    def embeddings(self, model: str, text: str) -> List[float]:
        """Generate embeddings for text"""
        payload = {
            "model": model,
            "prompt": text
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json().get("embedding", [])
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Embeddings error: {e}")
            return []
    
    def get_system_info(self) -> Dict:
        """Get Ollama system information"""
        try:
            # Get version info
            version_response = self.session.get(f"{self.base_url}/api/version")
            version_info = version_response.json() if version_response.status_code == 200 else {}
            
            # Get running models
            ps_response = self.session.get(f"{self.base_url}/api/ps")
            running_models = ps_response.json() if ps_response.status_code == 200 else {}
            
            return {
                "version": version_info,
                "running_models": running_models,
                "health": self.is_healthy()
            }
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}