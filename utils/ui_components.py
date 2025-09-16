import streamlit as st
import time
from typing import Dict, Any

def render_left_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### System Status")
        
        # Check system status
        status = st.session_state.qa_engine.get_system_status()
        
        # Ollama connection status
        if status['ollama_connected']:
            st.markdown('**Ollama**: Connected')
        else:
            st.markdown('**Ollama**: Disconnected')
            st.warning("Please make sure Ollama is running")
        
        # Model availability status
        if status['model_available']:
            st.markdown('**Model**: gemma:2b available')
        else:
            st.markdown('**Model**: gemma:2b not found')
            st.warning("Run: ollama pull gemma:2b")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Document information
        if st.session_state.document_uploaded:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("### Document Info")
            
            if hasattr(st.session_state, 'document_metadata'):
                metadata = st.session_state.document_metadata
                st.write(f"**File**: {metadata.get('filename', 'Unknown')}")
                st.write(f"**Type**: {metadata.get('file_type', 'Unknown')}")
                
                if metadata.get('file_type') == 'PDF':
                    st.write(f"**Pages**: {metadata.get('pages', 0)}")
                elif metadata.get('file_type') == 'Excel':
                    st.write(f"**Sheets**: {metadata.get('sheet_count', 0)}")
                
                # Show file size in readable format
                size_bytes = metadata.get('file_size', 0)
                if size_bytes > 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                elif size_bytes > 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                else:
                    size_str = f"{size_bytes} bytes"
                st.write(f"**Size**: {size_str}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Controls section
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### Controls")
        
        if st.button("Clear Chat History", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.session_state.qa_engine.clear_history()
            st.rerun()
        
        if st.session_state.document_uploaded:
            if st.button("Upload New Document", use_container_width=True, key="new_doc"):
                st.session_state.document_uploaded = False
                st.session_state.document_content = ""
                st.session_state.messages = []
                st.session_state.qa_engine.clear_history()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sample questions
        if st.session_state.document_uploaded:
            render_sample_questions()

def render_file_upload_center():
    st.markdown('<div class="file-upload-container">Upload your file below.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose a financial document",
        type=['pdf', 'xlsx', 'xls'],
        help="Upload PDF or Excel files containing financial statements",
        label_visibility="collapsed",
        key="file_uploader"
    )
    
    if uploaded_file is not None and not st.session_state.document_uploaded:
        if st.session_state.document_processor.validate_file(uploaded_file):
            with st.spinner("Processing document..."):
                try:
                    content, metadata = st.session_state.document_processor.process_document(uploaded_file)
                    if content:
                        st.session_state.document_content = content
                        st.session_state.document_metadata = metadata
                        st.session_state.document_uploaded = True
                        st.success("Document processed successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to extract content from document")
                except Exception as e:
                    st.error(f"Error processing document: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_sample_questions():
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### Sample Questions")
    
    # Generate sample questions
    sample_questions = st.session_state.qa_engine.generate_sample_questions(
        st.session_state.document_content
    )
    
    for i, question in enumerate(sample_questions[:5]):  # Show only 5
        if st.button(
            f"{question}",
            key=f"sample_q_{i}",
            use_container_width=True,
            help="Click to ask this question"
        ):
            # Add question to chat
            st.session_state.messages.append({"role": "user", "content": question})
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_chat_interface():
    # Show document status
    st.markdown("""
    <div style="background: #dcfce7; border: 1px solid #16a34a; border-radius: 8px; padding: 12px; margin-bottom: 20px;">
        <span class="status-indicator status-online"></span>
        <strong>Document loaded and ready for questions!</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Create chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="user-message">👤 {message["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="assistant-message">🤖 {message["content"]}</div>',
                    unsafe_allow_html=True
                )
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your financial document..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        st.markdown(
            f'<div class="user-message">👤 {prompt}</div>',
            unsafe_allow_html=True
        )
        
        # Show typing indicator
        with st.spinner("🤖 Analyzing document and generating response..."):
            # Get conversation context
            context = st.session_state.qa_engine.get_conversation_context()
            
            # Generate response
            response = st.session_state.qa_engine.generate_response(
                prompt,
                st.session_state.document_content,
                context
            )
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Rerun to show the new message
            st.rerun()

def render_document_summary():
    if st.session_state.document_uploaded and hasattr(st.session_state, 'document_metadata'):
        with st.expander("Document Summary", expanded=False):
            summary = st.session_state.document_processor.get_document_summary(
                st.session_state.document_content,
                st.session_state.document_metadata
            )
            st.text(summary)
            
            # Show extracted financial metrics if available
            metadata = st.session_state.document_metadata
            if 'extracted_metrics' in metadata and metadata['extracted_metrics']:
                st.markdown("**Financial Terms Found:**")
                metrics = metadata['extracted_metrics']
                for term, values in metrics.items():
                    if term != 'years' and values:
                        st.write(f"- **{term.title()}**: {len(values)} occurrences")
                if 'years' in metrics:
                    st.write(f"- **Years**: {', '.join(metrics['years'])}")

def show_error_message(error_type: str, message: str):
    error_styles = {
        'connection': ('🔌', '#ef4444'),
        'model': ('🤖', '#f59e0b'),
        'processing': ('📄', '#ef4444'),
        'general': ('❌', '#ef4444')
    }
    
    icon, color = error_styles.get(error_type, error_styles['general'])
    
    st.markdown(f"""
    <div style="background: #fef2f2; border-left: 4px solid {color}; padding: 12px; margin: 10px 0; border-radius: 4px;">
        <strong>{icon} {message}</strong>
    </div>
    """, unsafe_allow_html=True)

def show_success_message(message: str):
    st.markdown(f"""
    <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 12px; margin: 10px 0; border-radius: 4px;">
        <strong>{message}</strong>
    </div>
    """, unsafe_allow_html=True)

def render_loading_indicator(message: str = "Processing..."):
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <div style="display: inline-block; width: 20px; height: 20px; border: 3px solid #e2e8f0; border-radius: 50%; border-top-color: #3b82f6; animation: spin 1s ease-in-out infinite;"></div>
        <p style="margin-top: 10px; color: #64748b;">{message}</p>
    </div>
    <style>
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)

def render_metrics_display(metrics: Dict[str, Any]):
    if not metrics:
        return
    
    st.markdown("### Extracted Financial Metrics")
    
    cols = st.columns(3)
    col_idx = 0
    
    for metric_name, values in metrics.items():
        if isinstance(values, list) and values:
            with cols[col_idx % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{metric_name.title()}</h4>
                    <p><strong>{len(values)}</strong> occurrences found</p>
                </div>
                """, unsafe_allow_html=True)
            col_idx += 1

def format_file_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes} bytes"

