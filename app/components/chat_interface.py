import streamlit as st
import time
from datetime import datetime
from typing import List, Dict

class ChatInterface:
    """Advanced chat interface with history and formatting"""
    
    def __init__(self):
        self.max_history = 50  # Maximum chat history items
    
    def display_chat_history(self, chat_history: List[Dict]):
        """Display formatted chat history"""
        if not chat_history:
            st.info("💬 Start a conversation by asking a question about your documents!")
            return
        
        # Display recent chats first
        for i, chat in enumerate(reversed(chat_history[-self.max_history:])):
            with st.container():
                # Question
                st.markdown(f"**🙋 You ({self._format_timestamp(chat['timestamp'])}):**")
                st.markdown(f"> {chat['question']}")
                
                # Response
                st.markdown(f"**🤖 Assistant ({chat.get('model', 'unknown')}):**")
                st.markdown(chat['response'])
                
                # Context toggle
                with st.expander("📖 View Source Context", expanded=False):
                    st.text_area(
                        "Context used for this response:",
                        chat['context'],
                        height=150,
                        key=f"context_{i}_{chat['timestamp']}"
                    )
                
                st.markdown("---")
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp for display"""
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%H:%M:%S")
    
    def export_chat(self, chat_history: List[Dict]) -> str:
        """Export chat history to text"""
        export_text = "# Chat History Export\n\n"
        
        for i, chat in enumerate(chat_history):
            timestamp = self._format_timestamp(chat['timestamp'])
            export_text += f"## Q{i+1} ({timestamp})\n"
            export_text += f"**Question:** {chat['question']}\n\n"
            export_text += f"**Answer:** {chat['response']}\n\n"
            export_text += f"**Model:** {chat.get('model', 'unknown')}\n\n"
            export_text += "---\n\n"
        
        return export_text