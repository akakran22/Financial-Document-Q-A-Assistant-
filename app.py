import streamlit as st
import time
from utils.document_processor import DocumentProcessor
from utils.qa_engine import QAEngine
from utils.ui_components import render_left_sidebar, render_chat_interface, render_file_upload_center
import os

# Page configuration
st.set_page_config(
    page_title="Financial Document Q&A Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #1e3a8a;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.chat-container {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-radius: 15px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.user-message {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
    padding: 12px 18px;
    border-radius: 20px 20px 5px 20px;
    margin: 10px 0;
    margin-left: 20%;
    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
}

.assistant-message {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    color: #1e293b;
    padding: 12px 18px;
    border-radius: 20px 20px 20px 5px;
    margin: 10px 0;
    margin-right: 20%;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.file-upload-container {
    background: white;
    border: 2px dashed #cbd5e1;
    border-radius: 15px;
    padding: 30px;
    text-align: center;
    margin: 20px 0;
    transition: all 0.3s ease;
}

.file-upload-container:hover {
    border-color: #3b82f6;
    background: #f8fafc;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border-left: 4px solid #10b981;
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-online {
    background-color: #10b981;
}

.status-offline {
    background-color: #ef4444;
}

.sidebar-section {
    background: white;
    border-radius: 10px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Hide default streamlit elements */
.stDeployButton {
    visibility: hidden;
}

#MainMenu {
    visibility: hidden;
}

.stFooter {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    if 'qa_engine' not in st.session_state:
        st.session_state.qa_engine = QAEngine()
    if 'document_uploaded' not in st.session_state:
        st.session_state.document_uploaded = False
    if 'document_content' not in st.session_state:
        st.session_state.document_content = ""
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = ""

def main():
    initialize_session_state()
    
    # Left sidebar with system controls
    render_left_sidebar()
    
    # Header
    st.markdown('<h1 class="main-header">💼 Financial Document Q&A Assistant</h1>', unsafe_allow_html=True)
    
    # Main chat interface
    st.markdown("### Chat with Your Financial Data")
    if st.session_state.document_uploaded:
        render_chat_interface()
    else:
        st.markdown("""
        <div class="chat-container">
            <div style="text-align: center; padding: 40px;">
                <h3>Welcome to Financial Q&A Assistant</h3>
                <p>Please upload a financial document (PDF or Excel) below to start asking questions about your financial data.</p>
                <div style="margin: 20px 0;">
                    <span class="status-indicator status-offline"></span>
                    <span>No document uploaded</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload in center
        render_file_upload_center()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem;">
        <p>Powered by Ollama & Gemma 2B | Built with Streamlit</p>
        <p>Upload your financial documents and ask questions in natural language!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
