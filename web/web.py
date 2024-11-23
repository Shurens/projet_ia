import requests
import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from jose import jwt, JWTError 
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') 
API_URL = os.getenv('API_URL')


def format_date(date_str):
    # Convertir la chaîne en objet datetime en supposant qu'elle est en UTC
    utc_date = datetime.fromisoformat(date_str)
    # Ajuster pour le fuseau horaire (ajout de +1 heure par exemple)
    local_date = utc_date + timedelta(hours=1)
    # Formater la date pour un affichage plus lisible
    return local_date.strftime("%d-%m-%Y %H:%M")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'access_token' not in session:
            return redirect(url_for('login'))        
        try:
            # Décoder le token actuel pour vérifier son expiration
            decoded_token = jwt.decode(session['access_token'], app.secret_key, algorithms=["HS256"])
            exp_timestamp = decoded_token.get('exp')
            if exp_timestamp:
                expiration_time = datetime.fromtimestamp(exp_timestamp)
                remaining_time = expiration_time - datetime.utcnow()
                # Si le temps restant est inférieur à 15 minutes, rafraîchir le token
                if remaining_time < timedelta(minutes=15):
                    refresh_url = f"{API_URL}/refresh_token"
                    response = requests.post(refresh_url, headers={"Authorization": f"Bearer {session['access_token']}"})                    
                    if response.status_code == 200:
                        new_token_data = response.json()
                        new_access_token = new_token_data['access_token']                                                
                        # Stocker le nouveau token et la nouvelle expiration dans la session
                        session['access_token'] = new_access_token
                    else:
                        return redirect(url_for('logout'))                    
        except JWTError:
            return redirect(url_for('logout'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier si l'utilisateur est connecté
        if 'access_token' not in session:
            return redirect(url_for('login'))        
        try:
            # Décoder le token actuel pour vérifier son expiration
            decoded_token = jwt.decode(session['access_token'], app.secret_key, algorithms=["HS256"])
            exp_timestamp = decoded_token.get('exp')
            if exp_timestamp:
                expiration_time = datetime.fromtimestamp(exp_timestamp)
                remaining_time = expiration_time - datetime.utcnow()
                # Si le temps restant est inférieur à 15 minutes, rafraîchir le token
                if remaining_time < timedelta(minutes=15):
                    refresh_url = f"{API_URL}/refresh_token"
                    response = requests.post(refresh_url, headers={"Authorization": f"Bearer {session['access_token']}"} )                    
                    if response.status_code == 200:
                        new_token_data = response.json()
                        new_access_token = new_token_data['access_token']                                               
                        # Stocker le nouveau token dans la session
                        session['access_token'] = new_access_token
                    else:
                        return redirect(url_for('logout'))
            # Vérifier si l'utilisateur est administrateur (role est dans la session)
            if session.get('role') != 'admin':
                return "Accès refusé : vous n'êtes pas administrateur", 403        
        except JWTError:
            return redirect(url_for('logout'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        token_url = f"{API_URL}/token"
        
        response = requests.post(token_url, data={'username': username, 'password': password})
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            decoded_token = jwt.decode(access_token, app.secret_key, algorithms=["HS256"])

            session['access_token'] = access_token
            session['username'] = decoded_token.get("username")
            session['id'] = decoded_token.get("id")
            session['role'] = decoded_token.get("role")
            
            return redirect(url_for('home'))
        else:
            return "Échec de la connexion: Nom d'utilisateur ou mot de passe incorrect"
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Supprimer toutes les données de la session (y compris le token)
    session.clear()
    # Rediriger l'utilisateur vers la page de connexion
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Récupérer les données envoyées via le formulaire d'inscription
        username = request.form['username']
        password = request.form['password']
        
        # URL de la route FastAPI pour la création de l'utilisateur
        register_url = f"{API_URL}/user/create_user?username={username}&password={password}"

        
        # Préparer les données à envoyer
        data = {
            'username': username,
            'password': password
        }

        response = requests.post(register_url, data=data)

        # Vérifier la réponse de l'API
        if response.status_code == 200:
            # Utilisateur créé avec succès, rediriger vers la page de connexion
            return redirect(url_for('login'))
        else:
            # En cas d'échec, afficher un message d'erreur (ou gérer comme nécessaire)
            return f"Erreur lors de l'inscription, veuillez réessayer. {response.text}", 400
    return render_template('register.html')  # Afficher le formulaire d'inscription

@app.route('/')
@login_required
def home():
    # Récupérer le pseudo directement depuis la session
    username = session.get('username')
    # URL pour récupérer les 5 derniers commentaires via FastAPI
    get_comments_url = f"{API_URL}/comments/get_latest_comments"

    # Effectuer la requête pour obtenir les derniers commentaires
    comments_response = requests.get(get_comments_url, headers={"Authorization": f"Bearer {session['access_token']}"})
    
    if comments_response.status_code == 200:
        comments_data = comments_response.json()
        for comment in comments_data:
            comment["c_date"] = format_date(comment["c_date"])
    else:
        comments_data = []

    return render_template('home.html', username=username, API_URL=API_URL, comments=comments_data)
    

@app.route('/film/<int:film_id>', methods=['GET', 'POST'])
@login_required
def get_film(film_id):
    film_url = f"{API_URL}/film/{film_id}"
    film_response = requests.get(film_url, headers={"Authorization": f"Bearer {session['access_token']}"})
    
    get_comments_url = f"{API_URL}/comments/get_comments_by_film_id/{film_id}"
    comments_response = requests.get(get_comments_url, headers={"Authorization": f"Bearer {session['access_token']}"})
    if film_response.status_code == 200:
        film_data = film_response.json()

        # Check if the comments response contains actual comments or a detail message
        if comments_response.status_code == 200:
            comments_data = comments_response.json()
            for comment in comments_data:
                comment["c_date"] = format_date(comment["c_date"])

            # If the API returns a dictionary with "detail", set comments to an empty list
            comments = comments_data if isinstance(comments_data, list) else []
        else:
            comments = []  # No comments found or error retrieving them

        # Handle the POST request to add a new comment
        if request.method == 'POST':
            comment = request.form['comment']
            user_id = session.get('id')
            create_comment_url = f"{API_URL}/comments/create_comment"
            params = {
                'user_id': user_id,
                'film_id': film_id,
                'comment': comment
            }
            requests.post(create_comment_url, headers={"Authorization": f"Bearer {session['access_token']}"}, params=params)
            # Redirect after adding the comment to avoid form resubmission
            return redirect(url_for('get_film', film_id=film_id))
        
        # Render the template with film details and comments
        return render_template('film.html', film=film_data['film'], comments=comments)
    
    return "Film non trouvé", 404

@app.route('/prediction', methods=['GET', 'POST'])
@login_required
def prediction():
    if request.method == 'POST':
        # Récupération des données du formulaire
        budget = request.form.get('budget', type=int)
        revenue = request.form.get('revenue', type=int)
        runtime = request.form.get('runtime', type=int)
        vote_count = request.form.get('vote_count', type=int)
        
        # Préparer les données pour l'API
        prediction_url = f"{API_URL}/predict"
        headers = {"Authorization": f"Bearer {session['access_token']}"}
        params = {
            "budget": budget,
            "revenue": revenue,
            "runtime": runtime,
            "vote_count": vote_count
        }
        
        # Envoyer la requête à l'API pour obtenir une prédiction
        response = requests.post(prediction_url, headers=headers, params=params)
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            prediction_result = response.json()
        else:
            prediction_result = "Erreur lors de la prédiction"

        # Rendre la page avec le résultat de la prédiction
        return render_template('prediction.html', prediction_result=prediction_result)

    # Si méthode GET, afficher le formulaire vide
    return render_template('prediction.html')

@app.route('/dashboard_users')
@admin_required
def dashboard_users():
    # URL pour récupérer la liste des utilisateurs
    users_url = f"{API_URL}/user/get_all_users"
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    response = requests.get(users_url, headers=headers)
    return render_template('dashboard_users.html', users=response.json(), API_URL=API_URL)


@app.route('/session')
def show_session():
    # Afficher les détails de la session, y compris le temps restant pour le token
    if 'token_expiration' in session:
        expiration_time = datetime.fromtimestamp(session['token_expiration'])
        remaining_time = expiration_time - datetime.utcnow()
        
        session_data = dict(session)
        session_data['remaining_time'] = str(remaining_time)
    else:
        session_data = dict(session)
        session_data['remaining_time'] = "Durée d'expiration non disponible"

    return jsonify(session_data)





if __name__ == '__main__':
    app.run(debug=True)
