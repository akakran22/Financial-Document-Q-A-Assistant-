import requests
import json
import streamlit as st
from typing import Dict, List, Optional
import re

class QAEngine:
    def __init__(self, model_name: str = "gemma:2b", ollama_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.conversation_history = []

    def check_ollama_connection(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def check_model_availability(self) -> bool:
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                model_names = [model['name'] for model in models.get('models', [])]
                return self.model_name in model_names
            return False
        except requests.exceptions.RequestException:
            return False

    def generate_response(self, question: str, document_content: str, context: str = "") -> str:
        if not self.check_ollama_connection():
            return "❌ Error: Cannot connect to Ollama. Please make sure Ollama is running on your system."

        if not self.check_model_availability():
            return f"❌ Error: Model '{self.model_name}' not found. Please make sure you have downloaded the model using: ollama pull {self.model_name}"

        try:
            prompt = self._create_financial_prompt(question, document_content, context)

            # Make request to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "max_tokens": 500
                    }
                },
                timeout=180
            )

            if response.status_code == 200:
                result = response.json()
                answer = result.get('response', '').strip()
                
                # Post-process the answer
                answer = self._post_process_answer(answer)
                
                # Update conversation history
                self._update_conversation_history(question, answer)
                
                return answer
            else:
                return f"❌ Error: Ollama returned status code {response.status_code}"

        except requests.exceptions.Timeout:
            return "❌ Error: Request timed out. The model might be taking too long to respond."
        except requests.exceptions.RequestException as e:
            return f"❌ Error: Failed to connect to Ollama: {str(e)}"
        except Exception as e:
            return f"❌ Error: An unexpected error occurred: {str(e)}"

    def _create_financial_prompt(self, question: str, document_content: str, context: str) -> str:
        # Limit document content to prevent token overflow
        max_content_length = 3000
        if len(document_content) > max_content_length:
            document_content = document_content[:max_content_length] + "...[content truncated]"

        prompt = f"""You are a professional financial analyst assistant. Analyze the financial document content provided and answer questions accurately and concisely.

FINANCIAL DOCUMENT CONTENT:
{document_content}

CONVERSATION CONTEXT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on the information in the provided document
2. If the information is not in the document, clearly state that
3. Provide specific numbers and figures when available
4. Use professional financial terminology
5. Be concise but comprehensive
6. Format numbers properly (use commas for thousands, proper currency symbols)
7. If asked about trends, compare different periods if data is available

ANSWER:"""

        return prompt

    def _post_process_answer(self, answer: str) -> str:
        """Post-process the generated answer"""
        # Remove any potential prompt leakage
        answer = re.sub(r'^.*?ANSWER:\s*', '', answer, flags=re.DOTALL)
        
        # Clean up formatting
        answer = answer.strip()
        
        # Add financial formatting if numbers are detected
        answer = self._format_financial_numbers(answer)
        
        return answer

    def _format_financial_numbers(self, text: str) -> str:
        """Format financial numbers in the text"""
        # Pattern to match numbers that might need formatting
        number_pattern = r'\b(\d+(?:,\d{3})*(?:\.\d{2})?)\b'
        
        def format_number(match):
            number = match.group(1)
            # Add basic formatting if needed
            return number
        
        return re.sub(number_pattern, format_number, text)

    def _update_conversation_history(self, question: str, answer: str):
        self.conversation_history.append({
            'question': question,
            'answer': answer
        })
        
        # Keep only last 3 exchanges to manage context size
        if len(self.conversation_history) > 3:
            self.conversation_history.pop(0)

    def get_conversation_context(self) -> str:
        if not self.conversation_history:
            return ""
        
        context = "Previous conversation:\n"
        for i, exchange in enumerate(self.conversation_history[-2:], 1):  # Last 2 exchanges
            context += f"Q{i}: {exchange['question']}\n"
            context += f"A{i}: {exchange['answer'][:200]}...\n\n"
        
        return context

    def generate_sample_questions(self, document_content: str) -> List[str]:
        sample_questions = [
            "What is the total revenue for the latest period?",
            "What are the main expense categories?",
            "What is the net profit/loss?",
            "How has performance changed compared to the previous period?",
            "What are the key financial highlights?",
        ]
        
        # Try to generate more specific questions based on content
        specific_questions = []
        if 'revenue' in document_content.lower():
            specific_questions.append("What is the breakdown of revenue by category?")
        if 'expense' in document_content.lower():
            specific_questions.append("What are the largest expense items?")
        if any(year in document_content for year in ['2023', '2024', '2022']):
            specific_questions.append("Compare financial performance across different years")
        if 'cash flow' in document_content.lower():
            specific_questions.append("What is the cash flow situation?")
        
        # Combine and return unique questions
        all_questions = sample_questions + specific_questions
        return list(set(all_questions))[:8]  # Return max 8 questions

    def clear_history(self):
        self.conversation_history = []

    def get_system_status(self) -> Dict[str, bool]:
        return {
            'ollama_connected': self.check_ollama_connection(),
            'model_available': self.check_model_availability()
        }
