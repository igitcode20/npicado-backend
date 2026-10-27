from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
import os
import shutil
from pypdf import PdfReader
from datetime import datetime

from app.database import users_collection, documents_collection
from app.auth import verify_password, create_access_token, get_current_user
from app.models import GenerateRequest
from app.gemini_service import query_gemini_with_context
from app.document_generator import create_word_doc, create_excel_doc, create_pdf_doc

app = FastAPI(title="NPICADO_IA Backend")

# Configuración de CORS amplia para desarrollo y producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)