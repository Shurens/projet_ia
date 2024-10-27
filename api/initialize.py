from dto.connection_mysql import Connexion
from dto.auth import get_password_hash
import pandas as pd
from dotenv import load_dotenv
import os

class DatabaseInitializer(Connexion):

    @classmethod
    def create_user(cls):
        try:
            cls.connexion()
            load_dotenv()

            # Create admin user
            admin_username = os.getenv('ADMIN_USERNAME')
            admin_password = os.getenv('ADMIN_PASSWORD')
            admin_role = 'admin'
            admin_hashed_password = get_password_hash(admin_password)
            admin_query = "INSERT INTO users (u_user, u_pwd, u_category) VALUES (%s, %s, %s)"
            cls.cursor.execute(admin_query, (admin_username, admin_hashed_password, admin_role))
            print(f"Utilisateur '{admin_username}' créé avec succès avec un mot de passe haché.")
            
            # Create regular user
            user_username = os.getenv('USER_USERNAME')
            user_password = os.getenv('USER_PASSWORD')
            user_role = 'user'
            user_hashed_password = get_password_hash(user_password)
            user_query = "INSERT INTO users (u_user, u_pwd, u_category) VALUES (%s, %s, %s)"
            cls.cursor.execute(user_query, (user_username, user_hashed_password, user_role))
            print(f"Utilisateur '{user_username}' créé avec succès avec un mot de passe haché.")
            
            cls.bdd.commit()
        except Exception as e:
            print(f"Erreur lors de la création de l'utilisateur : {e}")
        finally:
            cls.deconnexion()
    
    @classmethod
    def insert_film_data(cls, csv_file='./data.csv'):
        """Méthode pour insérer la data des films dans la table films"""
        try:
            cls.connexion()  
            data = pd.read_csv(csv_file)
            print(f"{len(data)} lignes lues à partir du fichier CSV.")

            for index, row in data.iterrows():
                query = """
                INSERT INTO films (f_original_title, f_budget, f_revenue, f_runtime, f_vote_count, f_evaluation)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                values = (
                    row['original_title'], row['budget'], row['revenue'],
                    row['runtime'], row['vote_count'], row['evaluation']
                )
                cls.cursor.execute(query, values)

            cls.bdd.commit()  
            print("Données de films insérées avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'insertion des données de films : {e}")
        finally:
            cls.deconnexion()  

if __name__ == "__main__":
    DatabaseInitializer.insert_film_data()  
    DatabaseInitializer.create_user()
