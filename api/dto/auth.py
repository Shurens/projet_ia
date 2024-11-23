from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

# Configurations pour JWT
SECRET_KEY = os.getenv('SECRET_KEY')  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modèle pour le token
class Token(BaseModel):
    access_token: str
    token_type: str

# Modèle utilisateur pour représenter un utilisateur tel qu'il est en base de données
class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    role: str


# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Hachage du mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Durée de vie du token
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(username: str):
    from dto.requetes_bdd import Data
    result = Data.get_user_by_username(username)
    if result:
        print(f"Hachage du mot de passe : {result['u_pwd']}")  
        # Récupérer l'ID de l'utilisateur dans la base de données et le renvoyer avec les autres informations
        return User(id=result['u_id'], username=result['u_user'], hashed_password=result['u_pwd'], role=result['u_category'])
    return None




def authenticate_user(username: str, password: str):
    user = get_user(username)  
    if not user or not verify_password(password, user.hashed_password):
        return False, None
    return user  



def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username, "role": user.role, "id": user.id},  
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Fonction pour générer un nouveau token à partir des données d'un ancien token
def refresh_access_token(token: str):
    try:
        # Décoder le token actuel
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        user_id = payload.get("id")
        role = payload.get("role")

        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Créer un nouveau token avec les mêmes données utilisateur mais une nouvelle expiration
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_token = create_access_token(
            data={"username": username, "role": role, "id": user_id},
            expires_delta=expires_delta
        )
        return {"access_token": new_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

