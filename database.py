from pymongo import MongoClient
from pymongo.database import Database

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db: Database = client["delivery_system"]

# Коллекции
parcels_collection = db["parcels"]
albums_collection = db["albums"]

def get_database():
    """Получить объект базы данных"""
    return db