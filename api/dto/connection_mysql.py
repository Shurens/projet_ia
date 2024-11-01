import mysql.connector as mysqlpyth

class Connexion :

    @classmethod
    def connexion(cls):
        cls.bdd = mysqlpyth.connect(user='shuren', password='userpw', host='db', database='db_films')
        cls.cursor = cls.bdd.cursor(dictionary=True)

    @classmethod
    def deconnexion(cls):
        cls.cursor.close()
        cls.bdd.close()