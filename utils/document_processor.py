import pandas as pd
import PyPDF2
import streamlit as st
from io import BytesIO
import re
from typing import Dict, List, Tuple, Any

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.xlsx', '.xls']
        self.financial_keywords = [
            'revenue', 'income', 'profit', 'loss', 'expenses', 'cost',
            'assets', 'liabilities', 'equity', 'cash', 'flow', 'balance',
            'statement', 'earnings', 'ebitda', 'gross', 'net', 'operating', 'total'
        ]

    def process_document(self, uploaded_file) -> Tuple[str, Dict[str, Any]]:
        try:
            file_extension = uploaded_file.name.lower().split('.')[-1]
            if file_extension == 'pdf':
                return self._process_pdf(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                return self._process_excel(uploaded_file)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
            return "", {}

    def _process_pdf(self, uploaded_file) -> Tuple[str, Dict[str, Any]]:
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.getvalue()))
            text_content = ""
            
            for page_num, page in enumerate(pdf_reader.pages):
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += page.extract_text()

            metadata = {
                'file_type': 'PDF',
                'pages': len(pdf_reader.pages),
                'file_size': len(uploaded_file.getvalue()),
                'filename': uploaded_file.name
            }

            # Extract financial metrics
            financial_data = self._extract_financial_metrics(text_content)
            metadata.update(financial_data)

            return text_content, metadata

        except Exception as e:
            raise Exception(f"PDF processing error: {str(e)}")

    def _process_excel(self, uploaded_file) -> Tuple[str, Dict[str, Any]]:
        try:
            # Read all sheets
            excel_data = pd.read_excel(uploaded_file, sheet_name=None)
            text_content = ""

            for sheet_name, df in excel_data.items():
                text_content += f"\n--- Sheet: {sheet_name} ---\n"
                # Convert DataFrame to readable text
                text_content += df.to_string(index=False)
                text_content += "\n\n"

                # Add summary statistics for numerical columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    text_content += f"Numerical Summary for {sheet_name}:\n"
                    text_content += df[numeric_cols].describe().to_string()
                    text_content += "\n\n"

            metadata = {
                'file_type': 'Excel',
                'sheets': list(excel_data.keys()),
                'sheet_count': len(excel_data),
                'file_size': len(uploaded_file.getvalue()),
                'filename': uploaded_file.name
            }

            # Extract financial metrics
            financial_data = self._extract_financial_metrics_from_excel(excel_data)
            metadata.update(financial_data)

            return text_content, metadata

        except Exception as e:
            raise Exception(f"Excel processing error: {str(e)}")

    def _extract_financial_metrics(self, text: str) -> Dict[str, Any]:
        metrics = {}
        
        # Pattern to find monetary values
        money_pattern = r'[\$€£¥]?[\d,]+\.?\d*[MmKkBb]?'
        
        # Search for common financial terms with values
        for keyword in self.financial_keywords:
            pattern = rf'{keyword}[:\s]+({money_pattern})'
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                metrics[keyword] = matches

        # Extract years (for financial statements)
        year_pattern = r'\b(20\d{2})\b'
        years = list(set(re.findall(year_pattern, text)))
        if years:
            metrics['years'] = sorted(years, reverse=True)

        return {'extracted_metrics': metrics}

    def _extract_financial_metrics_from_excel(self, excel_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        metrics = {}
        
        for sheet_name, df in excel_data.items():
            sheet_metrics = {}
            
            # Look for financial keywords in column names
            financial_columns = []
            for col in df.columns:
                if any(keyword in str(col).lower() for keyword in self.financial_keywords):
                    financial_columns.append(col)
            
            if financial_columns:
                sheet_metrics['financial_columns'] = financial_columns
                
                # Extract numerical summaries for financial columns
                for col in financial_columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        sheet_metrics[col] = {
                            'sum': df[col].sum() if not df[col].isna().all() else 0,
                            'mean': df[col].mean() if not df[col].isna().all() else 0,
                            'max': df[col].max() if not df[col].isna().all() else 0,
                            'min': df[col].min() if not df[col].isna().all() else 0
                        }
            
            metrics[sheet_name] = sheet_metrics

        return {'sheet_metrics': metrics}

    def validate_file(self, uploaded_file) -> bool:
        if uploaded_file is None:
            return False

        file_extension = f".{uploaded_file.name.lower().split('.')[-1]}"
        if file_extension not in self.supported_formats:
            st.error(f"Unsupported file format. Please upload: {', '.join(self.supported_formats)}")
            return False

        # Check file size (limit to 200MB as mentioned in UI)
        if uploaded_file.size > 200 * 1024 * 1024:
            st.error("File size too large. Please upload a file smaller than 200MB.")
            return False

        return True

    def get_document_summary(self, content: str, metadata: Dict[str, Any]) -> str:
        summary = f"Document: {metadata.get('filename', 'Unknown')}\n"
        summary += f"Type: {metadata.get('file_type', 'Unknown')}\n"
        summary += f"Size: {metadata.get('file_size', 0)} bytes\n"

        if metadata.get('file_type') == 'PDF':
            summary += f"Pages: {metadata.get('pages', 0)}\n"
        elif metadata.get('file_type') == 'Excel':
            summary += f"Sheets: {metadata.get('sheet_count', 0)}\n"

        # Add extracted metrics summary
        if 'extracted_metrics' in metadata:
            metrics = metadata['extracted_metrics']
            if metrics:
                summary += "\nFound financial terms:\n"
                for term, values in metrics.items():
                    if term != 'years' and values:
                        summary += f"- {term.title()}: {len(values)} instances\n"

        return summary
