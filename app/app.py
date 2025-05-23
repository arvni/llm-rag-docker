import streamlit as st
import os
import sys
import logging
from pathlib import Path
import time
import psutil
import GPUtil

# Add components to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from components.document_processor import DocumentProcessor
from components.ollama_client import OllamaClient
from components.model_manager import ModelManager
from components.chat_interface import ChatInterface
from components.monitoring import SystemMonitor
from utils.file_handler import FileHandler
from utils.vector_store import VectorStoreManager

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "/app/data/chroma_db")
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/app/uploads")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Advanced RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/rag-system',
        'Report a bug': 'https://github.com/your-repo/rag-system/issues',
        'About': """
        # Advanced RAG System
        A comprehensive Document Q&A system powered by local LLMs.
        
        **Features:**
        - GPU-accelerated inference
        - OCR support for scanned documents
        - Advanced document processing
        - Real-time monitoring
        - Model management
        """
    }
)

# Custom CSS
with open('/app/static/style.css', 'r') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

class RAGSystemApp:
    def __init__(self):
        self.initialize_components()
        self.setup_session_state()
    
    def initialize_components(self):
        """Initialize all system components"""
        try:
            self.ollama_client = OllamaClient(OLLAMA_URL)
            self.document_processor = DocumentProcessor()
            self.model_manager = ModelManager(self.ollama_client)
            self.chat_interface = ChatInterface()
            self.system_monitor = SystemMonitor()
            self.file_handler = FileHandler(UPLOAD_PATH)
            self.vector_store_manager = VectorStoreManager(VECTOR_DB_PATH)
            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            st.error(f"System initialization error: {e}")
    
    def setup_session_state(self):
        """Setup session state variables"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.chat_history = []
            st.session_state.processed_docs = []
            st.session_state.current_model = None
            st.session_state.vectorstore = None
            st.session_state.system_stats = {}
    
    def render_header(self):
        """Render application header"""
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if os.path.exists('/app/static/logo.png'):
                st.image('/app/static/logo.png', width=100)
        
        with col2:
            st.title("🤖 Advanced RAG System")
            st.markdown("*Intelligent Document Q&A with Local LLM*")
        
        with col3:
            st.metric("System Status", 
                     "🟢 Online" if self.ollama_client.is_healthy() else "🔴 Offline")
    
    def render_sidebar(self):
        """Render sidebar with all controls"""
        with st.sidebar:
            st.header("🎛️ Control Panel")
            
            # System Status
            self.render_system_status()
            
            # Model Management
            self.render_model_management()
            
            # Document Management
            self.render_document_management()
            
            # Settings
            self.render_settings()
            
            # System Info
            self.render_system_info()
    
    def render_system_status(self):
        """Render system status section"""
        with st.expander("📊 System Status", expanded=True):
            status = self.system_monitor.get_system_status()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("CPU", f"{status['cpu_percent']:.1f}%")
                st.metric("RAM", f"{status['memory_percent']:.1f}%")
            
            with col2:
                st.metric("GPU", f"{status['gpu_percent']:.1f}%" if status['gpu_percent'] else "N/A")
                st.metric("VRAM", f"{status['gpu_memory']:.1f}%" if status['gpu_memory'] else "N/A")
            
            # Ollama status
            if self.ollama_client.wait_for_ollama(timeout=5):
                st.success("✅ Ollama Connected")
            else:
                st.error("❌ Ollama Disconnected")
                if st.button("🔄 Retry Connection"):
                    st.rerun()
    
    def render_model_management(self):
        """Render model management section"""
        with st.expander("🤖 Model Management"):
            available_models = self.ollama_client.list_models()
            
            if available_models:
                st.success(f"✅ {len(available_models)} Models Available")
                
                # Model selection
                selected_model = st.selectbox(
                    "Active Model:",
                    available_models,
                    key="model_selector"
                )
                st.session_state.current_model = selected_model
                
                # Model info
                model_info = self.model_manager.get_model_info(selected_model)
                if model_info:
                    st.json(model_info)
            else:
                st.warning("⚠️ No models installed")
            
            # Install new models
            st.subheader("Install Models")
            new_models = [
                "llama3.1:8b", "llama3.1:70b", "codellama:7b", 
                "mistral:7b", "phi3:mini", "gemma:7b", "qwen2:7b"
            ]
            
            model_to_install = st.selectbox("Choose model:", new_models)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Install", key="install_model"):
                    self.install_model(model_to_install)
            
            with col2:
                if st.button("🗑️ Remove", key="remove_model"):
                    self.remove_model(selected_model if available_models else None)
    
    def render_document_management(self):
        """Render document management section"""
        with st.expander("📄 Document Management", expanded=True):
            # File upload
            uploaded_files = st.file_uploader(
                "Upload Documents",
                type=['pdf', 'txt', 'docx', 'png', 'jpg', 'jpeg'],
                accept_multiple_files=True,
                help="Supports PDF, TXT, DOCX, and image files"
            )
            
            if uploaded_files:
                st.info(f"📁 {len(uploaded_files)} files selected")
                
                # Processing options
                ocr_enabled = st.checkbox("Enable OCR", value=True)
                chunk_size = st.slider("Chunk Size", 500, 2000, 1000)
                chunk_overlap = st.slider("Chunk Overlap", 50, 500, 200)
                
                if st.button("🔄 Process Documents", type="primary"):
                    self.process_documents(uploaded_files, ocr_enabled, chunk_size, chunk_overlap)
            
            # Existing documents
            if st.session_state.vectorstore:
                st.success("✅ Document database loaded")
                
                doc_count = self.vector_store_manager.get_document_count()
                st.metric("Documents", doc_count)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Search Test"):
                        self.test_vector_search()
                
                with col2:
                    if st.button("🗑️ Clear DB"):
                        self.clear_vector_database()
    
    def render_settings(self):
        """Render settings section"""
        with st.expander("⚙️ Settings"):
            # Generation settings
            st.subheader("Generation Settings")
            temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
            top_p = st.slider("Top P", 0.0, 1.0, 0.9, 0.1)
            top_k = st.slider("Top K", 1, 100, 40, 1)
            max_tokens = st.slider("Max Tokens", 100, 4000, 1000, 100)
            
            # Search settings
            st.subheader("Search Settings")
            similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, 0.1)
            max_results = st.slider("Max Search Results", 1, 10, 3, 1)
            
            # Store settings in session state
            st.session_state.generation_settings = {
                'temperature': temperature,
                'top_p': top_p,
                'top_k': top_k,
                'max_tokens': max_tokens
            }
            
            st.session_state.search_settings = {
                'similarity_threshold': similarity_threshold,
                'max_results': max_results
            }
    
    def render_system_info(self):
        """Render system information"""
        with st.expander("ℹ️ System Info"):
            info = self.system_monitor.get_detailed_info()
            
            st.json({
                "Python Version": info['python_version'],
                "Streamlit Version": info['streamlit_version'],
                "CUDA Available": info['cuda_available'],
                "GPU Count": info['gpu_count'],
                "Total RAM": f"{info['total_memory']:.1f} GB",
                "Available Storage": f"{info['available_storage']:.1f} GB"
            })
    
    def render_main_content(self):
        """Render main content area"""
        if not st.session_state.current_model:
            st.warning("🤖 Please select a model from the sidebar to start")
            return
        
        if not st.session_state.vectorstore:
            st.info("📚 Upload and process documents to enable Q&A")
            return
        
        # Chat interface
        self.render_chat_interface()
    
    def render_chat_interface(self):
        """Render the chat interface"""
        st.header("💬 Chat with Your Documents")
        
        # Chat history
        chat_container = st.container()
        
        # Input area
        with st.container():
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                user_question = st.text_input(
                    "Ask a question:",
                    placeholder="What is the main topic of the documents?",
                    key="user_input"
                )
            
            with col2:
                ask_button = st.button("🚀 Ask", type="primary")
            
            with col3:
                clear_button = st.button("🗑️ Clear")
        
        # Process question
        if ask_button and user_question:
            self.process_question(user_question)
        
        if clear_button:
            st.session_state.chat_history = []
            st.rerun()
        
        # Display chat history
        with chat_container:
            self.chat_interface.display_chat_history(st.session_state.chat_history)
    
    def process_question(self, question):
        """Process user question and generate response"""
        try:
            with st.spinner("🔍 Processing question..."):
                # Search for relevant documents
                search_results = self.vector_store_manager.similarity_search(
                    question, 
                    k=st.session_state.search_settings['max_results']
                )
                
                # Generate context
                context = "\n\n".join([doc.page_content for doc in search_results])
                
                # Generate response
                response = self.ollama_client.generate(
                    model=st.session_state.current_model,
                    prompt=question,
                    context=context,
                    **st.session_state.generation_settings
                )
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "question": question,
                    "response": response,
                    "context": context,
                    "timestamp": time.time(),
                    "model": st.session_state.current_model
                })
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Error processing question: {e}")
            logger.error(f"Question processing error: {e}")
    
    def process_documents(self, uploaded_files, ocr_enabled, chunk_size, chunk_overlap):
        """Process uploaded documents"""
        try:
            with st.spinner("📄 Processing documents..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process each file
                all_documents = []
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Processing {file.name}...")
                    
                    documents = self.document_processor.process_file(
                        file, 
                        ocr_enabled=ocr_enabled,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                    
                    all_documents.extend(documents)
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                # Create vector store
                status_text.text("Creating vector database...")
                vectorstore = self.vector_store_manager.create_vectorstore(all_documents)
                st.session_state.vectorstore = vectorstore
                
                # Update processed docs list
                st.session_state.processed_docs.extend([f.name for f in uploaded_files])
                
                progress_bar.progress(1.0)
                status_text.text("✅ Processing complete!")
                
                st.success(f"📚 Processed {len(uploaded_files)} documents with {len(all_documents)} chunks")
                time.sleep(2)
                st.rerun()
                
        except Exception as e:
            st.error(f"Error processing documents: {e}")
            logger.error(f"Document processing error: {e}")
    
    def install_model(self, model_name):
        """Install a new model"""
        try:
            with st.spinner(f"📥 Installing {model_name}..."):
                success = self.model_manager.install_model(model_name)
                if success:
                    st.success(f"✅ {model_name} installed successfully!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to install {model_name}")
        except Exception as e:
            st.error(f"Installation error: {e}")
            logger.error(f"Model installation error: {e}")
    
    def remove_model(self, model_name):
        """Remove a model"""
        if not model_name:
            st.warning("No model selected")
            return
        
        try:
            with st.spinner(f"🗑️ Removing {model_name}..."):
                success = self.model_manager.remove_model(model_name)
                if success:
                    st.success(f"✅ {model_name} removed successfully!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to remove {model_name}")
        except Exception as e:
            st.error(f"Removal error: {e}")
            logger.error(f"Model removal error: {e}")
    
    def test_vector_search(self):
        """Test vector search functionality"""
        try:
            test_query = "test search"
            results = self.vector_store_manager.similarity_search(test_query, k=3)
            st.info(f"Found {len(results)} results for test query")
            
            if results:
                with st.expander("Search Results"):
                    for i, result in enumerate(results):
                        st.text(f"Result {i+1}: {result.page_content[:200]}...")
        except Exception as e:
            st.error(f"Search test failed: {e}")
    
    def clear_vector_database(self):
        """Clear the vector database"""
        try:
            self.vector_store_manager.clear_database()
            st.session_state.vectorstore = None
            st.session_state.processed_docs = []
            st.success("🗑️ Database cleared successfully!")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Error clearing database: {e}")
    
    def run(self):
        """Main application runner"""
        try:
            self.render_header()
            self.render_sidebar()
            self.render_main_content()
            
            # Auto-refresh system stats every 30 seconds
            if st.session_state.initialized:
                time.sleep(0.1)  # Small delay to prevent too frequent updates
                
        except Exception as e:
            st.error(f"Application error: {e}")
            logger.error(f"Application runtime error: {e}")

def main():
    """Application entry point"""
    try:
        app = RAGSystemApp()
        app.run()
    except Exception as e:
        st.error(f"Failed to start application: {e}")
        logger.critical(f"Application startup failed: {e}")

if __name__ == "__main__":
    main()