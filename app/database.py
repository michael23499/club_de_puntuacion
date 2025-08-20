from pymongo import MongoClient
from bson import ObjectId

# Configura la conexión a MongoDB
MONGODB_URL = "mongodb://localhost:27017/"  
client = MongoClient(MONGODB_URL)

# Crea o accede a la base de datos
db = client["club_puntuacion"]

# Colecciones
clients_collection = db["clients"]  
establishments_collection = db["establishments"]
transactions_collection = db["transactions"]
administrators_collection = db["administrators"]  
sponsors_collection = db["sponsors"]  

# Verificación de la conexión
# print("DB:", db)  # conexión de la base de datos
# print("Clients Collection:", clients_collection)  # colección de clientes
# print("Establishments Collection:", establishments_collection)  # colección de establecimientos
# print("Administrators Collection:", administrators_collection)  # colección de administradores
# print("Sponsors Collection:", sponsors_collection)  # colección de patrocinadores