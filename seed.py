from app.database import users_collection
from app.auth import get_password_hash

def seed_database():
    # Limpia usuarios previos para evitar duplicados
    users_collection.delete_many({})
    
    # Definición de los 5 usuarios del sistema
    usuarios = [
        # --- 2 Administradores (Acceso total, ilimitado y a algoritmos) ---
        {
            "username": "Ismael",
            "hashed_password": get_password_hash("ismagit2006"),
            "role": "admin",
            "daily_tokens": 999999
        },
        {
            "username": "admin2",
            "hashed_password": get_password_hash("admin2026"),
            "role": "admin",
            "daily_tokens": 999999
        },

        # --- 3 Usuarios Normales (Mínimo 40 tokens/día, sin acceso a algoritmos) ---
        {
            "username": "usuario1",
            "hashed_password": get_password_hash("user1pass"),
            "role": "user",
            "daily_tokens": 40
        },
        {
            "username": "usuario2",
            "hashed_password": get_password_hash("user2pass"),
            "role": "user",
            "daily_tokens": 40
        },
        {
            "username": "usuario3",
            "hashed_password": get_password_hash("user3pass"),
            "role": "user",
            "daily_tokens": 40
        }
    ]
    
    users_collection.insert_many(usuarios)
    print("✓ Los 5 usuarios (2 Admins y 3 Usuarios normales) fueron registrados exitosamente en MongoDB.")

if __name__ == "__main__":
    seed_database()