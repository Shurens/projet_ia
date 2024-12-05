from dto.connection_mysql import Connexion
from dto.auth import get_password_hash

class Data(Connexion):
    """
    Classe Data pour interagir avec la base de données.
    Méthodes:
    ---------
    get_one_film(film_id):
        Récupère un film par son identifiant.
    get_all_films():
        Récupère tous les films avec certaines colonnes spécifiques.
    search_films_by_title(letters):
        Recherche des films par titre en utilisant des lettres données.
    get_user_by_username(username):
        Récupère un utilisateur par son nom d'utilisateur.
    toggle_user_category(user_id):
        Change la catégorie d'un utilisateur entre 'admin' et 'user'.
    get_all_users():
        Récupère tous les utilisateurs avec certaines colonnes spécifiques.
    user_exists(username):
        Vérifie si un utilisateur existe par son nom d'utilisateur.
    create_user(username, password):
        Crée un nouvel utilisateur avec un nom d'utilisateur et un mot de passe.
    delete_user(user_id):
        Supprime un utilisateur par son identifiant.
    create_comment(user_id, film_id, comment):
        Crée un commentaire pour un film par un utilisateur.
    get_comments_by_film_id(film_id):
        Récupère les commentaires d'un film par son identifiant.
    get_latest_comments():
        Récupère les derniers commentaires avec des informations sur l'utilisateur et le film.
    """

    @classmethod
    def get_one_film(cls, film_id):
        try:
            cls.connexion()
            query = "SELECT * FROM films WHERE f_id= %s"
            cls.cursor.execute(query, (film_id,))
            film = cls.cursor.fetchone()         
            return film
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
        finally:
            cls.deconnexion()

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
            cls.deconnexion()

    @classmethod
    def search_films_by_title(cls, letters: str):
        try:
            cls.connexion()
            query = "SELECT f_id, f_original_title FROM films WHERE f_original_title LIKE %s LIMIT 10"
            cls.cursor.execute(query, ('%' + letters + '%',))
            films = cls.cursor.fetchall() 
            return films
        except Exception as e:
            print(f"Erreur lors de la recherche des films : {e}")
        finally:
            cls.deconnexion()

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
            query = "SELECT u_category FROM users WHERE u_id = %s"
            cls.cursor.execute(query, (user_id,))
            result = cls.cursor.fetchone()

            if result is None:
                print(f"Utilisateur avec l'ID '{user_id}' non trouvé.")
                return {"message": "Utilisateur non trouvé"}

            current_role = result['u_category'] if result else None

            if current_role == 'admin':
                new_role = 'user'
            elif current_role == 'user':
                new_role = 'admin'
            else:
                print(f"Le rôle actuel '{current_role}' de l'utilisateur est inconnu.")
                return {"message": "Rôle inconnu"}

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
    def get_all_users(cls):
        try:
            cls.connexion()
            query = "SELECT u_id, u_user, u_category FROM users"
            cls.cursor.execute(query)
            users = cls.cursor.fetchall()
            return users
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs : {e}")
        finally:
            cls.deconnexion()

    @classmethod
    def user_exists(cls, username: str) -> bool:
        try:
            cls.connexion()
            query = "SELECT COUNT(*) AS count FROM users WHERE u_user = %s"
            cls.cursor.execute(query, (username,))
            count = cls.cursor.fetchone()
            return count['count'] > 0 
        except Exception as e:
            return False  
        finally:
            cls.deconnexion()

    @classmethod
    def create_user(cls, username: str, password: str):
        if cls.user_exists(username):
            return "user_exists" 

        try:
            cls.connexion()
            u_user = username
            u_pwd = password
            u_category = 'user'
            hashed_password = get_password_hash(u_pwd)
            query = "INSERT INTO users (u_user, u_pwd, u_category) VALUES (%s, %s, %s)"
            cls.cursor.execute(query, (u_user, hashed_password, u_category))
            cls.bdd.commit()
            return "success"  
        except Exception as e:
            return "error"  
        finally:
            cls.deconnexion()

    @classmethod
    def delete_user(cls, user_id: int):
        try:
            cls.connexion()
            query = "DELETE FROM users WHERE u_id = %s"
            cls.cursor.execute(query, (user_id,))
            cls.bdd.commit()

            
            if cls.cursor.rowcount > 0:
                print(f"Utilisateur avec l'ID '{user_id}' supprimé avec succès.")
                return True  
            else:
                print(f"Aucun utilisateur trouvé avec l'ID '{user_id}'.")
                return False 
        except Exception as e:
            print(f"Erreur lors de la suppression de l'utilisateur : {e}")
            return False
        finally:
            cls.deconnexion()

    @classmethod
    def create_comment(cls, user_id: int, film_id: int, comment: str):
        try:
            cls.connexion()
            query = "INSERT INTO commentaires (c_user_id, c_film_id, c_comment) VALUES (%s, %s, %s)"
            cls.cursor.execute(query, (user_id, film_id, comment))
            cls.bdd.commit()
            return "success" 
        except Exception as e:
            return "error"  
        finally:
            cls.deconnexion()

    @classmethod
    def get_comments_by_film_id(cls, film_id: int):
        try:
            cls.connexion()
            query = "SELECT u_user, c_comment, c_date FROM commentaires JOIN users ON u_id = c_user_id WHERE c_film_id = %s"
            cls.cursor.execute(query, (film_id,))
            comments = cls.cursor.fetchall()
            return comments
        except Exception as e:
            print(f"Erreur lors de la récupération des commentaires : {e}")
        finally:
            cls.deconnexion()

    @classmethod
    def get_latest_comments(cls):
        try:
            cls.connexion()
            query = "SELECT u_user, f_original_title, c_comment, c_date FROM commentaires JOIN users ON u_id = c_user_id JOIN films ON f_id = c_film_id ORDER BY c_date DESC LIMIT 5"
            cls.cursor.execute(query)
            comments = cls.cursor.fetchall()
            return comments
        except Exception as e:
            print(f"Erreur lors de la récupération des commentaires : {e}")
        finally:
            cls.deconnexion()