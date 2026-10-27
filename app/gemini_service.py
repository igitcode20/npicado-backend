from google import genai
from app.config import settings
from app.database import documents_collection

# Inicializar cliente oficial de Gemini
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def query_gemini_with_context(prompt: str) -> str:
    # 1. Traer el texto de todos los documentos cargados en MongoDB
    docs = list(documents_collection.find({}, {"_id": 0, "content": 1, "filename": 1}))
    context_text = "\n\n".join([f"--- Documento: {d['filename']} ---\n{d['content']}" for d in docs])
    
    # 2. Construir el prompt con la base de conocimiento integrada
    full_prompt = (
        f"Eres el motor de IA de la aplicación NPICADO_IA.\n"
        f"Usa la siguiente base de conocimiento interna almacenada en la base de datos para responder o estructurar la información:\n\n"
        f"CONTEXTO INTERNO DE DOCUMENTOS:\n{context_text}\n\n"
        f"SOLICITUD DEL USUARIO:\n{prompt}\n\n"
        f"Responde de manera clara, estructurada y detallada."
    )
    
    # 3. Generar respuesta con la API
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )
    return response.text