# main.py (updated and enhanced)
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import tempfile
import json
from datetime import datetime
import asyncio
from io import BytesIO
import uuid
import logging
import shutil

# Document processing imports
import PyPDF2
from docx import Document as DocxDocument
from PIL import Image
import pytesseract
import openai

# Database imports
import sqlite3
from sqlite3 import Connection
import aiosqlite

# Initialize FastAPI app
app = FastAPI(
    title="DocX Legal AI API",
    description="AI-powered legal document simplification service",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
SUPPORTED_FORMATS = ['.pdf', '.docx', '.txt', '.jpg', '.jpeg', '.png']
DATABASE_URL = "sqlite:///./docx_legal_ai.db"

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models
class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_text: str
    simplified_text: str
    language: str
    processing_time: float
    clause_count: int
    word_count: int
    status: str

class ChatMessage(BaseModel):
    message: str
    document_id: Optional[str] = None
    language: str = "en"

class ChatResponse(BaseModel):
    response: str
    confidence: float
    relevant_clauses: List[str]
    session_id: str

class SimplificationRequest(BaseModel):
    text: str
    target_language: str = "en"
    complexity_level: str = "simple"  # simple, intermediate, advanced

class UserRegistration(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

# Database setup
def init_db():
    with sqlite3.connect('docx_legal_ai.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                original_text TEXT,
                simplified_text TEXT,
                language TEXT,
                processing_time REAL,
                clause_count INTEGER,
                word_count INTEGER,
                status TEXT,
                upload_time TEXT,
                user_id TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                document_id TEXT,
                messages TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TEXT,
                last_login TEXT
            )
        ''')
        
        conn.commit()

# Initialize database
init_db()

# Helper Functions
class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        try:
            doc = DocxDocument(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing DOCX: {str(e)}")

    @staticmethod
    def extract_text_from_image(file_content: bytes) -> str:
        try:
            image = Image.open(BytesIO(file_content))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")

class AIService:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    async def simplify_legal_text(self, text: str, language: str = "en", complexity: str = "simple") -> str:
        """Simplify legal text using AI"""
        
        language_prompts = {
            "en": "Simplify this legal document into plain English",
            "hi": "इस कानूनी दस्तावेज़ को सरल हिंदी में समझाएं",
            "mr": "या कायदेशीर कागदपत्राचे मराठीत सोप्या भाषेत स्पष्टीकरण द्या"
        }
        
        complexity_levels = {
            "simple": "Use very simple language that a 12-year-old could understand",
            "intermediate": "Use clear language suitable for high school graduates",
            "advanced": "Use professional but clear language suitable for college graduates"
        }

        prompt = f"""
        {language_prompts.get(language, language_prompts["en"])}.
        
        {complexity_levels.get(complexity, complexity_levels["simple"])}.
        
        Please:
        1. Break down complex legal terms into simple explanations
        2. Explain what each clause means in practical terms
        3. Highlight key rights and obligations
        4. Use bullet points for clarity
        5. Maintain the document structure but make it readable
        
        Original legal text:
        {text[:4000]}  # Limit text to avoid token limits
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a legal expert who specializes in simplifying complex legal documents for ordinary people."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            # Fallback to rule-based simplification if AI fails
            return self.rule_based_simplification(text, language)

    def _chunk_text(self, text: str, chunk_size: int) -> List[str]:
        """Split text into manageable chunks for processing"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
            
        return chunks

    def rule_based_simplification(self, text: str, language: str) -> str:
        """Fallback rule-based simplification"""
        
        # Simple keyword replacement
        replacements = {
            "whereas": "given that",
            "heretofore": "before this",
            "hereinafter": "from now on",
            "aforementioned": "mentioned above",
            "pursuant to": "according to",
            "notwithstanding": "despite",
            "ipso facto": "by that very fact",
            "party of the first part": "first party",
            "party of the second part": "second party",
            "shall": "will",
            "hereby": "by this",
            "herein": "in this document",
            "thereof": "of that",
            "witnesseth": "shows that"
        }
    
        simplified = text
        for old, new in replacements.items():
            simplified = simplified.replace(old, new)
        
        return f"Simplified version: {simplified}"

    async def answer_question(self, question: str, document_text: str, language: str = "en") -> dict:
        """Answer questions about the document"""
        
        prompt = f"""
        Based on the following legal document, please answer this question: {question}
        
        Document content:
        {document_text[:3000]}
        
        Please provide:
        1. A clear, direct answer
        2. Reference to specific clauses if applicable
        3. Practical implications
        4. Any important warnings or considerations
        
        Answer in {language} language.
        """

        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful legal assistant. Provide accurate information based on the document, but always remind users to consult a lawyer for official legal advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return {
                "response": response.choices[0].message.content,
                "confidence": 0.85,
                "relevant_clauses": self.extract_relevant_clauses(document_text, question)
            }
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error processing your question: {str(e)}. Please try rephrasing your question or contact support.",
                "confidence": 0.0,
                "relevant_clauses": []
            }

    def extract_relevant_clauses(self, text: str, question: str) -> List[str]:
        """Extract clauses relevant to the question"""
        # Simple keyword matching - in production, use more sophisticated NLP
        question_words = question.lower().split()
        sentences = text.split('.')
        relevant = []
        
        for sentence in sentences[:20]:  # Limit to first 20 sentences
            if any(word in sentence.lower() for word in question_words):
                relevant.append(sentence.strip())
                
        return relevant[:3]  # Return top 3 relevant clauses

# Database helper functions
async def get_db_connection():
    conn = await aiosqlite.connect('docx_legal_ai.db')
    conn.row_factory = aiosqlite.Row
    return conn

async def save_document_to_db(document_data: dict):
    conn = await get_db_connection()
    try:
        await conn.execute('''
            INSERT INTO documents (id, filename, original_text, simplified_text, language, 
                                  processing_time, clause_count, word_count, status, upload_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            document_data['id'],
            document_data['filename'],
            document_data['original_text'],
            document_data['simplified_text'],
            document_data['language'],
            document_data['processing_time'],
            document_data['clause_count'],
            document_data['word_count'],
            document_data['status'],
            document_data['upload_time']
        ))
        await conn.commit()
    finally:
        await conn.close()

async def get_document_from_db(doc_id: str):
    conn = await get_db_connection()
    try:
        cursor = await conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        row = await cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'filename': row[1],
                'simplified_text': row[2],
                'status': row[3],
                'upload_time': row[4]
            }
        return None
    finally:
        await conn.close()

async def get_all_documents_from_db():
    conn = await get_db_connection()
    try:
        cursor = await conn.execute('SELECT id, filename, status, upload_time FROM documents ORDER BY upload_time DESC')
        rows = cursor.fetchall()
        
        documents = [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "upload_time": row[3]
            }
            for row in rows
        ]

        return {
            "documents": documents,
            "total_count": len(documents)
        }
    finally:
        await conn.close()

async def delete_document_from_db(doc_id: str):
    conn = await get_db_connection()
    try:
        await conn.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        await conn.commit()
    finally:
        await conn.close()

async def save_chat_session(session_id: str, document_id: str, messages: str):
    conn = await get_db_connection()
    try:
        await conn.execute('''
            INSERT OR REPLACE INTO chat_sessions (session_id, document_id, messages, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, document_id, messages, datetime.now().isoformat(), datetime.now().isoformat()))
        await conn.commit()
    finally:
        await conn.close()

async def get_chat_session(session_id: str):
    conn = await get_db_connection()
    try:
        cursor = await conn.execute('SELECT * FROM chat_sessions WHERE session_id = ?', (session_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None
    finally:
        await conn.close()

# Initialize AI service
ai_service = AIService()

# API Routes
@app.get("/")
async def root():
    return {
        "message": "DocX Legal AI API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "upload": "/upload-document",
            "simplify": "/simplify",
            "chat": "/chat",
            "health": "/health",
            "documents": "/documents",
            "stats": "/stats"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DocX Legal AI"
    }

@app.post("/upload-document")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = "en",
    complexity: str = "simple"
):
    """Upload and process a legal document"""
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Supported: {SUPPORTED_FORMATS}")

    try:
        # Read file content
        content = await file.read()
        
        # For text files, decode the content
        if file_ext == '.txt':
            text = content.decode('utf-8')
        else:
            # For PDF, we'd use PyPDF2 in a real implementation
            text = f"Content from {file.filename} would be extracted here."
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        simplified_text = ai_service.simplify_legal_text(text[:500])
        
        doc_data = {
            "id": doc_id,
            "filename": file.filename,
            "simplified_text": simplified_text,
            "status": "completed",
            "upload_time": datetime.now().isoformat()
        }
        
        save_document_to_db(doc_data)
        
        return {
            "id": doc_id,
            "filename": file.filename,
            "simplified_text": simplified_text,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def process_document_async(doc_id: str, filename: str, original_text: str, 
                               language: str, complexity: str, file_path: str):
    """Background task to process document"""
    try:
        # Simplify text using AI
        start_time = datetime.now()
        simplified_text = await ai_service.simplify_legal_text(original_text, language, complexity)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Store document
        doc_data = {
            "id": doc_id,
            "filename": filename,
            "original_text": original_text,
            "simplified_text": simplified_text,
            "language": language,
            "processing_time": processing_time,
            "clause_count": len([s for s in original_text.split('.') if len(s.strip()) > 20]),
            "word_count": len(original_text.split()),
            "upload_time": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Save to database
        await save_document_to_db(doc_data)
        
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            
        logger.info(f"Document {doc_id} processed successfully")
        
    except Exception as e:
        logger.error(f"Error in background processing for document {doc_id}: {str(e)}")
        
        # Save error status to database
        error_doc_data = {
            "id": doc_id,
            "filename": filename,
            "original_text": original_text,
            "simplified_text": f"Error processing document: {str(e)}",
            "language": language,
            "processing_time": 0,
            "clause_count": 0,
            "word_count": len(original_text.split()),
            "upload_time": datetime.now().isoformat(),
            "status": "error"
        }
        
        await save_document_to_db(error_doc_data)

@app.post("/simplify")
async def simplify_text(request: SimplificationRequest):
    """Simplify legal text directly"""
    
    try:
        simplified = await ai_service.simplify_legal_text(
            request.text, 
            request.target_language, 
            request.complexity_level
        )
        
        return {
            "original_text": request.text[:500] + "..." if len(request.text) > 500 else request.text,
            "simplified_text": simplified,
            "language": request.target_language,
            "complexity_level": request.complexity_level,
            "word_count_original": len(request.text.split()),
            "word_count_simplified": len(simplified.split())
        }
    except Exception as e:
        logger.error(f"Error simplifying text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error simplifying text: {str(e)}")

@app.post("/chat")
async def chat_with_document(message: ChatMessage):
    """Chat about a specific document"""
    
    try:
        # Get document if specified
        document_text = ""
        if message.document_id:
            doc_data = await get_document_from_db(message.document_id)
            if not doc_data:
                raise HTTPException(status_code=404, detail="Document not found")
            document_text = doc_data["original_text"]
        else:
            # General legal question without specific document
            document_text = "General legal knowledge base"
        
        # Get AI response
        response_data = await ai_service.answer_question(
            message.message, 
            document_text, 
            message.language
        )
        
        # Generate session ID
        session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(message.message) % 1000}"
        
        # Store chat session
        chat_data = {
            "user_message": message.message,
            "ai_response": response_data["response"],
            "timestamp": datetime.now().isoformat(),
            "document_id": message.document_id
        }
        
        await save_chat_session(session_id, message.document_id, json.dumps([chat_data]))
        
        response_data["session_id"] = session_id
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """Get document details"""
    
    doc_data = await get_document_from_db(doc_id)
    if not doc_data:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc_data

@app.get("/documents")
async def list_documents():
    """List all processed documents"""
    
    documents = await get_all_documents_from_db()
    
    return {
        "documents": [
            {
                "id": doc["id"],
                "filename": doc["filename"],
                "upload_time": doc["upload_time"],
                "language": doc["language"],
                "word_count": doc["word_count"],
                "status": doc["status"]
            }
            for doc in documents
        ],
        "total_count": len(documents)
    }

@app.delete("/document/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    
    doc_data = await get_document_from_db(doc_id)
    if not doc_data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    await delete_document_from_db(doc_id)
    return {"message": f"Document {doc_id} deleted successfully"}

@app.get("/languages")
async def get_supported_languages():
    """Get supported languages"""
    
    return {
        "languages": [
            {"code": "en", "name": "English", "native_name": "English"},
            {"code": "hi", "name": "Hindi", "native_name": "हिंदी"},
            {"code": "mr", "name": "Marathi", "native_name": "मराठी"}
        ]
    }

@app.get("/stats")
async def get_statistics():
    """Get application statistics"""
    
    documents = await get_all_documents_from_db()
    total_docs = len(documents)
    
    if total_docs == 0:
        return {
            "total_documents_processed": 0,
            "total_words_processed": 0,
            "average_processing_time_seconds": 0,
            "language_distribution": {},
            "status_distribution": {}
        }
    
    completed_docs = [doc for doc in documents if doc["status"] == "completed"]
    total_words_processed = sum(doc["word_count"] for doc in completed_docs)
    avg_processing_time = sum(doc["processing_time"] for doc in completed_docs) / len(completed_docs) if completed_docs else 0
    
    language_distribution = {}
    status_distribution = {}
    
    for doc in documents:
        lang = doc["language"]
        status = doc["status"]
        language_distribution[lang] = language_distribution.get(lang, 0) + 1
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    return {
        "total_documents_processed": total_docs,
        "total_words_processed": total_words_processed,
        "average_processing_time_seconds": round(avg_processing_time, 2),
        "language_distribution": language_distribution,
        "status_distribution": status_distribution
    }

# Serve static files (for frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )