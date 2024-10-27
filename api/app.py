import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from dto.requetes_bdd import Data
from dto.auth import login, Token, oauth2_scheme
from model.random_forest import Prediction

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
    }
]

app = FastAPI(
    title="Application pour les films",
    description="API de l'application de prédiction de notes de films",
    version="1.0.0",
    openapi_tags=tags
)

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
def create_user(username: str, password: str, token: str = Depends(oauth2_scheme)):
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

@app.post("/predict", tags=["Prediction"], description="Prédire la catégorie d'un film")
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
    # Les données à prédire doivent être fournies sous forme de liste [budget, revenue, runtime, vote_count]
    data = [budget, revenue, runtime, vote_count]
    prediction = Prediction.predict(data)    
    if "Erreur" in prediction:
        raise HTTPException(status_code=400, detail=prediction)
    return prediction  

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

if __name__ == "__main__" :
    uvicorn.run(app, host="localhost", port=8081)