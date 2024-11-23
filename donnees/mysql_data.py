from mysql_connection import MySQLAccess

class Data_mysql:
    def __init__(self):
        self.mysql = MySQLAccess()
        self.mysql.connexion()

    def get_films_data_mysql(self):
        try:
            # Exécute la requête pour récupérer toutes les données de collect_films
            query = "SELECT * FROM collect_films"
            self.mysql.cursor.execute(query)

            # Récupère les résultats
            films_list = self.mysql.cursor.fetchall()
        except Exception as e:
            print(f"Une erreur s'est produite lors de la récupération des données: {e}")
            films_list = []
        finally:
            self.mysql.deconnexion()      

        return films_list
