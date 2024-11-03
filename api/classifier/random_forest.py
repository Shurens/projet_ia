import pandas as pd
import joblib
import mlflow
import os

class Prediction:
        
    @classmethod
    def predict(cls, data):
        try:
            # Obtenir le chemin absolu du répertoire actuel
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # label_encoder_path = os.path.join(current_dir, "label_encoder_films.joblib")
            model_path = os.path.join(current_dir, "random_forest_model")

            # Charger le label encoder et le modèle
            label_encoder = joblib.load(label_encoder_path)
            model = mlflow.sklearn.load_model(model_path) 

            # Créer un DataFrame à partir des données d'une seule ligne et 4 colonnes
            df = pd.DataFrame([data], columns=["f_budget", "f_revenue", "f_runtime", "f_vote_count"])
            prediction_numeric = model.predict(df)
            prediction_label = label_encoder.inverse_transform(prediction_numeric.astype(int))
            return prediction_label[0]
        except Exception as e:
            return f"Erreur lors de la prédiction : {e}"
