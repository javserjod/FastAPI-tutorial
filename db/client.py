# con pymongo nos podemos conectar a MongoDB
from pymongo import MongoClient


# url por defecto es localhost
# db_client = MongoClient().local    # conexión BBDD local


# Base de datos remota
db_client = MongoClient(
    "mongodb+srv://test:test@cluster0.jraoiac.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
).test


# Así, tenemos server en local y base de datos en remoto