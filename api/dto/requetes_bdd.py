from dto.connection_mysql import Connexion
from dto.auth import get_password_hash

class Data(Connexion):

    @classmethod
    def get_one_film(cls, film_id):
        try:
            cls.connexion()
            query = "SELECT * FROM films WHERE f_id= %s"
            cls.cursor.execute(query, (film_id,))
            film = cls.cursor.fetchone() # Récupère un seul film          
            return film
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
        finally:
            cls.connexion()

    @classmethod
    def get_all_films(cls):
        try:
            cls.connexion()
            query = "SELECT f_budget, f_revenue, f_runtime, f_vote_count, f_evaluation FROM films"
            cls.cursor.execute(query)
            films = cls.cursor.fetchall()          
            return films
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
        finally:
            cls.connexion()

    @classmethod
    def get_user_by_username(cls, username: str):
        try:
            cls.connexion()
            query = "SELECT * FROM users WHERE u_user = %s"
            cls.cursor.execute(query, (username,))
            return cls.cursor.fetchone()  
        except Exception as e:
            print(f"Erreur lors de la récupération de l'utilisateur : {e}")
        finally:
            cls.deconnexion()

    @classmethod
    def toggle_user_category(cls, user_id: int):
        try:
            cls.connexion()
            # Récupérer le rôle actuel de l'utilisateur via l'ID
            query = "SELECT u_category FROM users WHERE u_id = %s"
            cls.cursor.execute(query, (user_id,))
            result = cls.cursor.fetchone()

            if result is None:
                print(f"Utilisateur avec l'ID '{user_id}' non trouvé.")
                return {"message": "Utilisateur non trouvé"}

            current_role = result['u_category'] if result else None

            # Déterminer le nouveau rôle
            if current_role == 'admin':
                new_role = 'user'
            elif current_role == 'user':
                new_role = 'admin'
            else:
                print(f"Le rôle actuel '{current_role}' de l'utilisateur est inconnu.")
                return {"message": "Rôle inconnu"}

            # Mise à jour du rôle dans la base de données
            update_query = "UPDATE users SET u_category = %s WHERE u_id = %s"
            cls.cursor.execute(update_query, (new_role, user_id))
            print(f"Rôle de l'utilisateur avec l'ID '{user_id}' mis à jour vers '{new_role}'.")
            cls.bdd.commit()
        except Exception as e:
            print(f"Erreur lors de la mise à jour du rôle de l'utilisateur : {e}")
            raise e
        finally:
            cls.deconnexion()

    @classmethod
    def user_exists(cls, username: str) -> bool:
        try:
            cls.connexion()
            query = "SELECT COUNT(*) AS count FROM users WHERE u_user = %s"
            cls.cursor.execute(query, (username,))
            count = cls.cursor.fetchone()
            return count['count'] > 0  # Retourne True si un utilisateur existe, False sinon
        except Exception as e:
            # En cas d'erreur, on suppose que l'utilisateur n'existe pas
            return False  
        finally:
            cls.deconnexion()

    @classmethod
    def create_user(cls, username: str, password: str):
        # Vérifiez d'abord si l'utilisateur existe déjà
        if cls.user_exists(username):
            return "user_exists"  # Utilisateur déjà existant

        try:
            cls.connexion()
            u_user = username
            u_pwd = password
            u_category = 'user'
            hashed_password = get_password_hash(u_pwd)
            query = "INSERT INTO users (u_user, u_pwd, u_category) VALUES (%s, %s, %s)"
            cls.cursor.execute(query, (u_user, hashed_password, u_category))
            cls.bdd.commit()
            return "success"  # Utilisateur créé avec succès
        except Exception as e:
            return "error"  # Erreur générale lors de la création
        finally:
            cls.deconnexion()

    @classmethod
    def delete_user(cls, user_id: int):
        try:
            cls.connexion()
            query = "DELETE FROM users WHERE u_id = %s"
            cls.cursor.execute(query, (user_id,))
            cls.bdd.commit()

            # Vérifiez le nombre de lignes affectées pour déterminer si la suppression a réussi
            if cls.cursor.rowcount > 0:
                print(f"Utilisateur avec l'ID '{user_id}' supprimé avec succès.")
                return True  # L'utilisateur a été supprimé
            else:
                print(f"Aucun utilisateur trouvé avec l'ID '{user_id}'.")
                return False  # Aucun utilisateur trouvé avec cet ID
        except Exception as e:
            print(f"Erreur lors de la suppression de l'utilisateur : {e}")
            return False  # En cas d'erreur
        finally:
            cls.deconnexion()

