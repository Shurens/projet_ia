import os
import mysql.connector
from dotenv import load_dotenv

class MySQLAccess:
    def __init__(self):
        env_path = os.path.join(os.path.dirname(__file__), 'bdd', '.env')
        load_dotenv(env_path)

        # Récupére les variables d'environnement
        self.__USER = os.getenv('MYSQL_USER')
        self.__PW = os.getenv('MYSQL_PASSWORD')
        self.__DB_NAME = os.getenv('MYSQL_DATABASE')
        self.__HOST = 'localhost'  

    def connexion(self):
        self.conn = mysql.connector.connect(
            host=self.__HOST,
            user=self.__USER,
            password=self.__PW,
            database=self.__DB_NAME
        )
        self.cursor = self.conn.cursor(dictionary=True)
        return self.conn

    def deconnexion(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
