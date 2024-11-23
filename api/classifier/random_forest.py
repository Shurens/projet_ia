import pandas as pd
import joblib
import mlflow
import os
import dagshub


class Prediction:
    
    @classmethod
    def predict(self, data):
        try:             
            DAGSHUB_TOKEN = os.getenv('DAGSHUB_TOKEN')

            mlflow.set_tracking_uri(f'https://{DAGSHUB_TOKEN}@dagshub.com/Shurens/my-first-repo.mlflow')

            # Charger le label encoder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            label_encoder_path = os.path.join(current_dir, "label_encoder_films.joblib")
            label_encoder = joblib.load(label_encoder_path)
   
            logged_model = 'runs:/36c90fa6113740db849a015d17c5d43c/random_forest_model'
            loaded_model = mlflow.pyfunc.load_model(logged_model)

            # Créer un DataFrame à partir des données d'une seule ligne et 4 colonnes
            df = pd.DataFrame([data], columns=["f_budget", "f_revenue", "f_runtime", "f_vote_count"])
            prediction_numeric = loaded_model.predict(df)
            prediction_label = label_encoder.inverse_transform(prediction_numeric.astype(int))
            return prediction_label[0]
        except Exception as e:
            return f"Erreur lors de la prédiction : {e}"   
                 
    @classmethod
    def test_model(self):
        try:
            DAGSHUB_TOKEN = os.getenv('DAGSHUB_TOKEN')
            mlflow.set_tracking_uri(f'https://{DAGSHUB_TOKEN}@dagshub.com/Shurens/my-first-repo.mlflow')
                                    
            # Charger le label encoder
            current_dir = os.path.dirname(os.path.abspath(__file__))
            label_encoder_path = os.path.join(current_dir, "label_encoder_films.joblib")
            label_encoder = joblib.load(label_encoder_path)
   
            logged_model = 'runs:/36c90fa6113740db849a015d17c5d43c/random_forest_model'
            loaded_model = mlflow.pyfunc.load_model(logged_model)

            # Charge les data de test du CSV 
            current_dir = os.path.dirname(os.path.abspath(__file__))
            test_data_path = os.path.join(current_dir, "test_data.csv")
            test_data = pd.read_csv(test_data_path)

            # Sépare les features des labels
            X_test = test_data[["f_budget", "f_revenue", "f_runtime", "f_vote_count"]]

            # Prédire les labels
            predictions_numeric = loaded_model.predict(X_test)

            # Convertir les labels numériques en labels textuels
            predictions_label = label_encoder.inverse_transform(predictions_numeric.astype(int))

            # Ajouter les prédictions au DataFrame de test
            test_data['predicted_evaluation'] = predictions_label

            # Compter le nombre de prédictions correct
            correct_predictions = (test_data['predicted_evaluation'] == test_data['f_evaluation']).sum()

            # Valide le modèle si au moins 7 prédictions sont correctes
            if correct_predictions >= 7:
                return f"Success : {correct_predictions} prédictions correctes"
            else:
                return f"Failure: {correct_predictions} prédictions correctes"
        except Exception as e:
            return f"Erreur lors de la validation du modèle : {e}"
