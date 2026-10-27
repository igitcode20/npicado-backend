from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
import os
import shutil
from pypdf import PdfReader
from datetime import datetime

from app.database import users_collection, documents_collection
from app.auth import verify_password, create_access_token, get_current_user, get_password_hash
from app.models import GenerateRequest
from app.gemini_service import query_gemini_with_context
from app.document_generator import create_word_doc, create_excel_doc, create_pdf_doc

app = FastAPI(title="NPICADO_IA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

# 1. Endpoint de Inicio de Sesión
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos.")
    
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user["role"],
        "username": user["username"],
        "daily_tokens": user["daily_tokens"]
    }

# 2. Endpoint de Generación con Control de Tokens y Roles
@app.post("/generate")
def generate_doc(req: GenerateRequest, current_user: dict = Depends(get_current_user)):
    is_admin = current_user["role"] == "admin"
    
    # Restricción: Algoritmos / Código solo para Administradores
    if req.file_type == "algorithm" and not is_admin:
        raise HTTPException(
            status_code=403, 
            detail="Acceso denegado: La generación de algoritmos o código es exclusiva para Administradores."
        )
    
    # Control de Tokens para usuarios normales (40 al día)
    if not is_admin:
        if current_user.get("daily_tokens", 0) <= 0:
            raise HTTPException(
                status_code=429, 
                detail="Has agotado tus 40 tokens diarios. Intenta de nuevo mañana."
            )
        # Descontar 1 token
        users_collection.update_one({"username": current_user["username"]}, {"$inc": {"daily_tokens": -1}})

    # Consultar información con Gemini + Contexto de MongoDB
    ai_response = query_gemini_with_context(req.prompt)
    
    # Generar el archivo en el formato deseado
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = ""
    
    if req.file_type == "pdf":
        file_path = create_pdf_doc(f"npicado_{timestamp}.pdf", ai_response)
    elif req.file_type == "word":
        file_path = create_word_doc(f"npicado_{timestamp}.docx", ai_response)
    elif req.file_type in ["excel", "algorithm"]:
        file_path = create_excel_doc(f"npicado_{timestamp}.xlsx", ai_response)
    else:
        file_path = create_pdf_doc(f"npicado_{timestamp}.pdf", ai_response)

    remaining_tokens = "Ilimitado" if is_admin else current_user["daily_tokens"] - 1

    return {
        "status": "success",
        "response_text": ai_response,
        "download_url": f"/download/{os.path.basename(file_path)}",
        "tokens_remaining": remaining_tokens
    }

# 3. Endpoint para Descargar los Archivos Generados
@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("generated", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="El archivo solicitado no existe.")

# 4. Endpoint para subir nuevos documentos e ir retroalimentando la IA
@app.post("/upload-knowledge")
def upload_knowledge(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    file_location = f"uploads/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    content = ""
    if file.filename.endswith(".pdf"):
        reader = PdfReader(file_location)
        for page in reader.pages:
            content += page.extract_text() or ""
    elif file.filename.endswith(".txt"):
        with open(file_location, "r", encoding="utf-8") as f:
            content = f.read()
            
    documents_collection.insert_one({
        "filename": file.filename,
        "uploaded_by": current_user["username"],
        "upload_date": datetime.utcnow(),
        "content": content
    })
    
    return {"message": f"Documento '{file.filename}' procesado e integrado a la base de datos."}