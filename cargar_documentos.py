import os
from datetime import datetime
from pypdf import PdfReader
from app.database import documents_collection

# Carpeta donde pegaste los 22 documentos
CARPETA_DOCUMENTOS = "mis_documentos"

def cargar_lote_inicial():
    if not os.path.exists(CARPETA_DOCUMENTOS):
        print(f"❌ La carpeta '{CARPETA_DOCUMENTOS}' no existe. Créala y pon ahí tus 22 archivos.")
        return

    archivos = os.listdir(CARPETA_DOCUMENTOS)
    if not archivos:
        print(f"⚠️ La carpeta '{CARPETA_DOCUMENTOS}' está vacía. Copia ahí tus 22 documentos.")
        return

    print(f"🔍 Procesando {len(archivos)} documentos...")
    cargados = 0

    for nombre_archivo in archivos:
        ruta_completa = os.path.join(CARPETA_DOCUMENTOS, nombre_archivo)
        contenido = ""

        # Extraer texto según la extensión
        try:
            if nombre_archivo.endswith(".pdf"):
                reader = PdfReader(ruta_completa)
                for page in reader.pages:
                    contenido += page.extract_text() or ""
            elif nombre_archivo.endswith(".txt"):
                with open(ruta_completa, "r", encoding="utf-8") as f:
                    contenido = f.read()
            else:
                print(f"⏭️ Omitido '{nombre_archivo}': Solo se leen archivos .pdf o .txt")
                continue

            # Guardar o actualizar en MongoDB
            documents_collection.update_one(
                {"filename": nombre_archivo},
                {
                    "$set": {
                        "filename": nombre_archivo,
                        "uploaded_by": "Ismael (Carga Inicial)",
                        "upload_date": datetime.utcnow(),
                        "content": contenido
                    }
                },
                upsert=True
            )
            cargados += 1
            print(f"  ✓ Cargado a MongoDB: {nombre_archivo}")

        except Exception as e:
            print(f"  ❌ Error al leer {nombre_archivo}: {e}")

    print(f"\n🎉 ¡Listo! Se subieron {cargados} documentos a la base de datos de MongoDB.")

if __name__ == "__main__":
    cargar_lote_inicial()