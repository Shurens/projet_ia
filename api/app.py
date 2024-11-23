import uvicorn
import time
import psutil
from prometheus_client import Summary, Counter, Gauge, generate_latest, Histogram
from starlette.responses import Response
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dto.requetes_bdd import Data
from dto.auth import login, refresh_access_token, Token, oauth2_scheme
from classifier.random_forest import Prediction
from fastapi.middleware.cors import CORSMiddleware


# Instanciation des métriques
REQUEST_TIME = Summary('request_processing_seconds', 'Temps passé à traiter les requêtes')
INFERENCES = Counter('model_inferences_total', 'Nombre total d\'inférences effectuées')
LATENCY = Gauge('model_latency_seconds', 'Latence du model en secondes')

OUTPUT_CATEGORY = Counter('model_output_category_count', 'Nombre de prédiction par catégorie', ['category'])


tags = [
    {
        "name": "Films",
        "description": "Requêtes sur la table 'films'"
    },
    {
        "name": "Users",
        "description": "Requêtes sur la table 'users'"
    },
    {
        "name": "Prediction",
        "description": "Prédiction de la catégorie d'un film"
    },
    {
        "name": "Commentaires",
        "description": "Requêtes sur la table 'commentaires'"
    },
    {
        "name": "Monitoring",
        "description": "Métriques pour Prometheus"
    }
]

app = FastAPI(
    title="Application pour les films",
    description="API de l'application de prédiction de notes de films",
    version="1.0.0",
    openapi_tags=tags
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",      
        "http://localhost:5000",      
        "http://host.docker.internal:5000"  # Accès depuis un conteneur
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP
    allow_headers=["*"],  # Autorise toutes les en-têtes
)

# Helper pour récupérer l'utilisation mémoire et CPU
def get_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss  # Mémoire résidente utilisée par le processus (en bytes)

def get_cpu_usage():
    return psutil.cpu_percent(interval=None)  # Utilisation CPU en pourcentage


@app.get("/all_films", tags=["Films"], description="Récupère tous les films")
def get_all_films(token: str = Depends(oauth2_scheme)):
    """
    Récupère toutes les données de tous les films de la base de données.
    Cette route nécessite un token d'authentification valide.
    Returns:
        dict: Un dictionnaire avec tous les films.
    """
    films = Data.get_all_films()
    if not films:
        raise HTTPException(status_code=404, detail="Aucun film trouvé")
    return {"films": films}

@app.get("/film/{film_id}", tags=["Films"], description="Récupère un film par son id")
def get_film_by_id(film_id: int, token: str = Depends(oauth2_scheme)):
    """
    Récupère un film de la base de données.
    Cette route nécessite un token d'authentification valide.
    Args:
        film_id (int): l'ID du film.
    Returns:
        dict: Un dictionnaire avec les informations du film.
    """
    film = Data.get_one_film(film_id)
    if not film:
        raise HTTPException(status_code=404, detail="Film non trouvé")
    return {"film": film}

@app.get("/search_films", tags=["Films"], description="Recherche de films par titre")
def search_film_by_letters(letters: str, token: str = Depends(oauth2_scheme)):
    """
    Recherche des films dont le titre correspond à la requête.
    Cette route nécessite un token d'authentification valide.
    Args:
        letters (str): Les premières lettres du titre du film.
    Returns:
        list: Une liste de films correspondant à la requête.
    """
    films = Data.search_films_by_title(letters)
    if not films:
        raise HTTPException(status_code=404, detail=f"Aucun film trouvé {letters}")
    return films

@app.get("/user/get_all_users", tags=["Users"], description="Récupère tous les utilisateurs")
def get_all_users(token: str = Depends(oauth2_scheme)):
    """
    Récupère tous les utilisateurs de la base de données.
    Cette route nécessite un token d'authentification valide.
    Returns:
        dict: Un dictionnaire avec tous les utilisateurs.
    """
    users = Data.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="Aucun utilisateur trouvé.")
    return {"users": users}

@app.put("/user/toggle_category/{user_id}/", tags=["Users"], description="Change le rôle d'un utilisateur")
def toggle_user_role(user_id: int, token: str = Depends(oauth2_scheme)):  
    """
    Change la catégorie d'un utilisateur de 'user' à 'admin' et vice-versa.
    Cette route nécessite un token d'authentification valide.
    Args:
        user_id (str): L'id de l'utilisateur dont la catégorie doit être modifiée.
    Returns:
        dict: Un message indiquant si le rôle a été changé avec succès ou si une erreur est survenue.
    """    
    role = Data.toggle_user_category(user_id)
    if role is None:
        return {"message": f"Le rôle de l'utilisateur '{user_id}' a été changé avec succès."}
    raise HTTPException(status_code=404, detail=f"Utilisateur avec l'ID '{user_id}' non trouvé.")
    
@app.post("/user/create_user", tags=["Users"], description="Crée un utilisateur")
def create_user(username: str, password: str):
    """
    Crée un nouvel utilisateur avec un nom d'utilisateur et un mot de passe haché.
    Cette route nécessite un token d'authentification valide.
    Args:
        username (str): Le nom d'utilisateur du nouvel utilisateur.
        password (str): Le mot de passe du nouvel utilisateur.
    Returns:
        dict: Un message indiquant si l'utilisateur a été créé avec succès ou si une erreur est survenue.
    """
    result = Data.create_user(username, password)
    if result == "success":
        return {"message": f"Utilisateur '{username}' créé avec succès."}
    elif result == "user_exists":
        raise HTTPException(status_code=400, detail=f"Erreur : l'utilisateur '{username}' existe déjà.")
    else:
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'utilisateur.")
    
@app.delete("/user/delete_user/{user_id}", tags=["Users"], description="Supprime un utilisateur par son ID")
def delete_user(user_id: int, token: str = Depends(oauth2_scheme)):
    """
    Supprime un utilisateur de la base de données en utilisant son ID.
    Args:
        user_id (int): L'ID de l'utilisateur à supprimer.
    Returns:
        dict: Un message indiquant si l'utilisateur a été supprimé avec succès ou non.
    """
    user_deleted = Data.delete_user(user_id)
    if user_deleted:  
        return {"message": f"Utilisateur avec l'ID '{user_id}' supprimé avec succès."}
    raise HTTPException(status_code=404, detail=f"Erreur lors de la suppression de l'utilisateur avec l'ID '{user_id}'.")

@app.post("/comments/create_comment", tags=["Commentaires"], description="Crée un commentaire pour un film")
def create_comment(user_id: int, film_id: int, comment: str, token: str = Depends(oauth2_scheme)):
    """
    Crée un commentaire pour un film donné.
    Args:
        user_id (int): L'ID de l'utilisateur qui a laissé le commentaire.
        film_id (int): L'ID du film pour lequel le commentaire est laissé.
        comment (str): Le texte du commentaire.
    Returns:
        dict: Un message indiquant si le commentaire a été créé avec succès ou non.
    """
    result = Data.create_comment(user_id, film_id, comment)
    if result == "success":
        return {"message": "Commentaire créé avec succès."}
    raise HTTPException(status_code=500, detail="Erreur lors de la création du commentaire.")

@app.get("/comments/get_comments_by_film_id/{film_id}", tags=["Commentaires"], description="Récupère les commentaires pour un film")
def get_comments_by_film_id(film_id: int, token: str = Depends(oauth2_scheme)):
    """
    Récupère les commentaires laissés pour un film donné.
    Args:
        film_id (int): L'ID du film pour lequel les commentaires sont récupérés.
    Returns:
        dict: Une liste de commentaires pour le film donné.
    """
    comments = Data.get_comments_by_film_id(film_id)
    if not comments:
        raise HTTPException(status_code=404, detail=f"Aucun commentaire trouvé pour le film avec l'ID '{film_id}'.")
    return comments


@app.get("/comments/get_latest_comments", tags=["Commentaires"], description="Récupère les derniers commentaires")
def get_latest_comments(token: str = Depends(oauth2_scheme)):
    """
    Récupère les derniers commentaires laissés pour tous les films.
    Cette route nécessite un token d'authentification valide.
    Returns:
        dict: Une liste des derniers commentaires pour chaque film.
    """
    comments = Data.get_latest_comments()
    if not comments:
        raise HTTPException(status_code=404, detail="Aucun commentaire trouvé.")
    return comments

@app.post("/predict", tags=["Prediction"], description="Prédire la catégorie d'un film")
@REQUEST_TIME.time()  # Mesurer le temps de traitement
def predict_film_category(budget: int, revenue: int, runtime: int, vote_count: int, token: str = Depends(oauth2_scheme)):
    """
    Prédire la catégorie d'un film basé sur 4 données.    
    Args:
        budget (int): Budget du film.
        revenue (int): Revenus générés par le film.
        runtime (int): Durée du film (en minutes).
        vote_count (int): Nombre de votes pour le film.    
    Returns:
        dict: La catégorie prédite pour le film.
    """
    start_time = time.time()
    

    # Suivre les métriques existantes
    INFERENCES.inc()  # Incrémenter le nombre d'inférences

    # Préparer les données
    data = [budget, revenue, runtime, vote_count]

    # Faire une prédiction
    prediction = Prediction.predict(data)

    # Si erreur dans la prédiction, lever une exception HTTP
    if "Erreur" in prediction:
        raise HTTPException(status_code=400, detail=prediction)

    # Si erreur dans la prédiction, lever une exception HTTP
    if isinstance(prediction, str):  # Vérifier si la prédiction est une chaîne
        category = prediction  # Utiliser directement la chaîne retournée
    else:
        raise HTTPException(status_code=400, detail="Erreur dans la prédiction.")

    # Calcul de la latence
    LATENCY.set(time.time() - start_time)

    # Enregistrer la métrique de la catégorie prédite
    OUTPUT_CATEGORY.labels(category).inc()

    return prediction

@app.get("/test_model", tags=["Prediction"], description="Tester le modèle de prédiction")
def test_model(token: str = Depends(oauth2_scheme)):
    """
    Tester le modèle de prédiction avec des données de test.
    Cette route nécessite un token d'authentification valide.
    Returns:
        str: Un message indiquant le succès ou l'échec du test du modèle.
    """
    result = Prediction.test_model()
    if "Erreur" in result or "Failure" in result:
        raise HTTPException(status_code=500, detail=result)
    return {"message": result}

@app.post("/token", response_model=Token)
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Route pour obtenir un token d'authentification.
    Args:
        username (str): Nom d'utilisateur.
        password (str): Mot de passe.
    """
    token_data = login(form_data)
    if not token_data:
        raise HTTPException(status_code=401, detail="Nom d'utilisateur ou mot de passe incorrect")
    return token_data

@app.post("/refresh_token", description="Rafraîchit le token d'authentification")
def refresh_token(token: str = Depends(oauth2_scheme)):
    """
    Rafraîchir un token d'authentification en prolongeant sa durée de vie.
    Cette route nécessite un token d'authentification valide.
    """
    return refresh_access_token(token)


@app.get("/metrics", tags=["Monitoring"], description="Exposer les métriques pour Prometheus")
def metrics():
    """
    Expose les métriques pour Prometheus.
    """
    return Response(content=generate_latest(), media_type="text/plain")


if __name__ == "__main__" :
    uvicorn.run(app, host="localhost", port=8081)