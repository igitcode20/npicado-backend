from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

# Colecciones de la base de datos
users_collection = db["users"]
documents_collection = db["documents"]
logs_collection = db["logs"]