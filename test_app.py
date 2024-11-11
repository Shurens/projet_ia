import sys
import os
from fastapi.testclient import TestClient
import pytest
# Chemin vers le dossier racine du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/api')
from api.app import app
client = TestClient(app)

def test_get_all_films():
    response = client.get("/all_films", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert "films" in response.json()

def test_get_film_by_id():
    response = client.get("/film/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    if "film" in json_response:
        assert "film" in json_response
    else:
        assert json_response["message"] == "Film non trouvé"

def test_toggle_user_role():
    response = client.put("/user/toggle_category/2", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    if "message" in json_response:
        assert "succès" in json_response["message"] or "non trouvé" in json_response["message"]

def test_create_user():
    response = client.post("/user/create_user", params={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    assert "créé avec succès" in json_response["message"] or "existe déjà" in json_response["message"]

def test_delete_user():
    response = client.delete("/user/delete_user/2", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    assert "supprimé avec succès" in json_response["message"] or "Erreur" in json_response["message"]

def test_predict_film_category():
    response = client.post("/predict", params={"budget": 1000000, "revenue": 5000000, "runtime": 120, "vote_count": 1000}, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    assert "message" not in json_response or "Erreur" not in json_response["message"]

def test_test_model():
    response = client.get("/test_model", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    assert "Success" in json_response["message"]

def test_token():
    response = client.post("/token", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"
    
def test_search_film_by_letters():
    response = client.get("/search_films", params={"letters": "Spot"}, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    assert isinstance(json_response, list)
    if json_response:
        assert "f_original_title" in json_response[1]

def test_create_comment():
    response = client.post("/comments/create_comment", params={"user_id": 1, "film_id": 1, "comment": "Bon film !"}, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    assert "message" in json_response
    assert "créé avec succès" in json_response["message"]

def test_get_comments_by_film_id():
    response = client.get("/comments/get_comments_by_film_id/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    json_response = response.json()
    assert isinstance(json_response, list)
    if json_response:
        assert "c_comment" in json_response[0]

def test_get_latest_comments():
    response = client.get("/comments/get_latest_comments", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200