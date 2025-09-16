# 💼 Financial Document Q&A Assistant

A powerful Streamlit application that allows users to upload financial documents (PDF or Excel) and ask questions about their financial data using natural language processing powered by Ollama and Gemma 2B model.

## ✨ Features

- **Document Upload**: Support for PDF and Excel files (up to 200MB)
- **Intelligent Q&A**: Ask questions about your financial data in natural language
- **Financial Metrics Extraction**: Automatically identifies and extracts key financial terms
- **Interactive Chat Interface**: Beautiful, responsive chat UI with conversation history
- **Sample Questions**: Auto-generated relevant questions based on document content
- **Real-time Status**: System status monitoring for Ollama connection and model availability
- **Document Summary**: Detailed overview of uploaded documents with extracted metrics

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Ollama** installed and running locally
3. **Gemma 2B model** downloaded in Ollama

### Installation Steps

1. **Clone or download the project**
   ```bash
   git clone <your-repo-url>
   cd financial-qa-assistant
   ```

2. **Install required Python packages**
   ```bash
   pip install streamlit pandas PyPDF2 requests openpyxl
   ```

3. **Install and setup Ollama**
   
   **For Windows:**
   - Download from [Ollama.ai](https://ollama.ai)
   - Run the installer
   - Open Command Prompt and run:
   ```bash
   ollama pull gemma:2b
   ```

   **For macOS:**
   ```bash
   brew install ollama
   ollama pull gemma:2b
   ```

   **For Linux:**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull gemma:2b
   ```

4. **Start Ollama service**
   ```bash
   ollama serve
   ```
   (Keep this terminal window open)

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## 📁 Project Structure

```
financial-qa-assistant/
├── app.py                     # Main Streamlit application
├── utils/
│   ├── __init__.py
│   ├── document_processor.py  # PDF and Excel processing logic
│   ├── qa_engine.py          # Ollama integration and Q&A logic
│   └── ui_components.py      # UI components and styling
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 Configuration

### Ollama Settings
The application uses these default settings:
- **Model**: `gemma:2b`
- **Ollama URL**: `http://localhost:11434`
- **Temperature**: 0.3
- **Max Tokens**: 500
- **Timeout**: 180 seconds

You can modify these settings in `utils/qa_engine.py`:

```python
class QAEngine:
    def __init__(self, model_name: str = "gemma:2b", ollama_url: str = "http://localhost:11434"):
        # Modify these values as needed
```

### File Upload Limits
- **Supported formats**: PDF, XLSX, XLS
- **Maximum file size**: 200MB
- **Content limit**: 3000 characters (automatically truncated)

## 📖 Usage Guide

### 1. Upload a Document
- Click the file upload area
- Select a PDF or Excel file containing financial data
- Wait for processing to complete

### 2. Ask Questions
Once your document is uploaded, you can ask questions like:
- "What is the total revenue for the latest period?"
- "What are the main expense categories?"
- "How has performance changed compared to the previous period?"
- "What is the net profit/loss?"

### 3. Use Sample Questions
The app automatically generates relevant questions based on your document content. Click on any sample question to ask it instantly.

### 4. View Document Summary
Expand the "Document Summary" section to see:
- File information (name, type, size)
- Extracted financial metrics
- Number of pages/sheets


### Custom Models
To use a different Ollama model, modify the `model_name` parameter:



**Built with ❤️ using Streamlit, Ollama, and Gemma 2B**

For more information about the underlying technologies:
- [Streamlit Documentation](https://docs.streamlit.io)
- [Ollama Documentation](https://ollama.ai/docs)
- [Gemma Model Information](https://ai.google.dev/gemma)
