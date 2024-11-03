import mysql.connector as mysqlpyth
from dotenv import load_dotenv
import os

class Connexion:

    @classmethod
    def connexion(cls):
        load_dotenv()
        user = os.getenv('MYSQL_USER')
        password = os.getenv('MYSQL_PASSWORD')
        host = os.getenv('MYSQL_HOST')
        database = os.getenv('MYSQL_DATABASE')
        
        cls.bdd = mysqlpyth.connect(user=user, password=password, host=host, database=database)
        cls.cursor = cls.bdd.cursor(dictionary=True)

    @classmethod
    def deconnexion(cls):
        cls.cursor.close()
        cls.bdd.close()