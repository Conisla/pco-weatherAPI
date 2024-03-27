from tensorflow import keras
from keras import layers
from sklearn.metrics import mean_squared_error
import math
from keras.models import load_model
import numpy as np


def create_linreg_model(shape, output_nb):
    # Définir le modèle de régression linéaire
    model = keras.Sequential([
        layers.Dense(output_nb, input_shape=[shape])
    ])

    # Compiler le modèle en utilisant l'optimiseur Adam 
    # et l'erreur quadratique moyenne comme fonction de perte
    model.compile(optimizer='adam', loss='mse')
    return model


def get_rrmse(df, mesured, predicted):
    rmse = np.sqrt(mean_squared_error(df[mesured], df[predicted]))

    rRMSE = round(rmse/df[mesured].mean()*100,2)

    return rRMSE

def load_keras_model(path_to_model):
    """
    Charge un modèle Keras à partir d'un chemin de fichier donné.
    """
    return load_model(path_to_model)

def prepare_input_data(raw_input_data):
    """
    Prépare les données d'entrée pour la prédiction. 
    Vous devrez peut-être ajuster cette fonction en fonction de la structure attendue par votre modèle.
    """
    # Exemple : convertit les données d'entrée en un np.array si les données d'entrée sont une liste.
    return np.array(raw_input_data)

def make_prediction(model, prepared_data):
    """
    Effectue une prédiction avec le modèle chargé et les données préparées.
    """
    prediction = model.predict(prepared_data)
    return prediction
