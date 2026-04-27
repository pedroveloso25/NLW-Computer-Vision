import urllib.request
import os
import pickle

def baixar_modelo_mediapipe(model_path='gesture_recognizer.task'):
    """Baixa o modelo do MediaPipe caso não exista localmente."""
    if not os.path.exists(model_path):
        print("Baixando o modelo de gestos do MediaPipe...")
        url = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'
        urllib.request.urlretrieve(url, model_path)
        print("Modelo baixado com sucesso!")
    return model_path

def carregar_modelo_customizado(model_path='modelo_gestos.pkl'):
    """Carrega o modelo treinado com scikit-learn (Pickle)."""
    with open(model_path, 'rb') as f:
        clf = pickle.load(f)
    return clf
