from pymongo import MongoClient
from dotenv import load_dotenv
import os

class MongoAccess : 
    env_path = os.path.join(os.path.dirname(__file__), 'bdd', '.env')
    load_dotenv(env_path)

    __USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
    __PW = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
    __DB_NAME = os.getenv("MONGO_INITDB_DATABASE")
    __COLLECTION_NAME = "films_mongo"
    

    @classmethod
    def connexion(cls) :
        cls.client = MongoClient(f"mongodb://{cls.__USER}:{cls.__PW}@localhost:27017")

        cls.db = cls.client[cls.__DB_NAME]
        cls.collection = cls.db[cls.__COLLECTION_NAME]

    @classmethod
    def deconnexion(cls) :
        cls.client.close()