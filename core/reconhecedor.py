import cv2
import mediapipe as mp
import numpy as np

# Mapeamento: nome do gesto resolvido → arquivo de imagem na pasta gestures/
GESTURE_IMAGE_MAP = {
    "Hangloose": "hangloose.png",
    "Rock": "rock.png",
    "Spock": "spock.png",
    "Heart": "heart.png",
    "Fck U": "fk.png.gif",
    "Thumb_Up": "joinha.png",
    "Victory": "peace.png",
    "Open_Palm": "absolute.png",
}

class ReconhecedorHibrido:
    def __init__(self, model_asset_path, clf_model):
        """
        Inicializa o reconhecedor híbrido de gestos.
        :param model_asset_path: Caminho para o modelo .task do MediaPipe.
        :param clf_model: Modelo treinado scikit-learn carregado.
        """
        self.clf = clf_model
        
        # Inicializando os módulos correspondentes do MediaPipe
        BaseOptions = mp.tasks.BaseOptions
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=model_asset_path),
            running_mode=VisionRunningMode.VIDEO, # Modo de vídeo (muito mais otimizado para sequências continuas e webcam)
            num_hands=2 
        )
        self.recognizer = GestureRecognizer.create_from_options(options)
        
        import time
        self.start_time = time.time() # Guardamos o momento inicial para os timestamps de vídeo
        
        # Módulos de desenho
        try:
            self.mp_hands = mp.tasks.vision.HandLandmarksConnections
            self.HAND_CONNECTIONS = self.mp_hands.HAND_CONNECTIONS
            self.mp_drawing = mp.tasks.vision.drawing_utils
            self.mp_drawing_styles = mp.tasks.vision.drawing_styles
        except AttributeError:
            self.mp_hands = mp.solutions.hands
            self.HAND_CONNECTIONS = self.mp_hands.HAND_CONNECTIONS
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_drawing_styles = mp.solutions.drawing_styles

        # Constantes
        self.MARGIN = 10 
        self.ROW_SIZE = 10 
        self.FONT_SIZE = 1
        self.FONT_THICKNESS = 1

    def processar_imagem(self, image):
        """
        Recebe uma imagem (numpy array em BGR) e retorna uma tupla com a imagem
        processada (apenas com landmarks) e a lista de labels (textos) detectados.
        """
        import time
        # OpenCV lê a imagem como BGR, converter para RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)
        
        # O modo de vídeo precisa do tempo exato atual do frame respectivo em MS
        timestamp_ms = int((time.time() - self.start_time) * 1000)

        # Realiza o reconhecimento (agora rastreando otimizado para vídeo/webcam)
        recognition_result = self.recognizer.recognize_for_video(mp_image, timestamp_ms)

        # Retorna a imagem original se não houver detecção
        if not recognition_result.hand_landmarks:
            return image, [], None

        labels = []
        resolved_gestures = []  # Gesto resolvido de cada mão

        # Percorre as mãos detectadas
        for i, hand_landmarks in enumerate(recognition_result.hand_landmarks):
            # 1. Predição do MediaPipe (Gestos Originais)
            mp_category = "None"
            mp_score = 0.0
            if recognition_result.gestures and i < len(recognition_result.gestures):
                if recognition_result.gestures[i]:
                    mp_category = recognition_result.gestures[i][0].category_name
                    mp_score = round(recognition_result.gestures[i][0].score, 2)

            # 2. Predição do Modelo Customizado
            row = []
            for landmark in hand_landmarks:
                row.extend([landmark.x, landmark.y, landmark.z])
                
            custom_category = self.clf.predict([row])[0]
            custom_prob = round(np.max(self.clf.predict_proba([row])[0]), 2)
            
            # 3. Lógica híbrida para exibir os resultados
            if mp_category != "None" and mp_category != "" and mp_score > 0.5:
                result_text = f'Original: {mp_category} ({mp_score})'
                color_css = "aqua" # Cyan em CSS para o frontend
                resolved_gesture = mp_category
            else:
                result_text = f'Novo: {custom_category} ({custom_prob})'
                color_css = "lime" # Verde em CSS para o frontend
                resolved_gesture = custom_category
            
            resolved_gestures.append(resolved_gesture)

            # Em vez de desenhar travando a CPU do backend, enviamos pro frontend
            labels.append({
                "text": result_text,
                "color": color_css,
                "x": 15,
                "y": 60 + (i * 40)
            })
            
            # Desenhando os landmarks
            self.mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                self.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )

        # Verifica se as duas mãos fazem o mesmo gesto
        gesture_image = None
        if len(resolved_gestures) == 2 and resolved_gestures[0] == resolved_gestures[1]:
            gesture_image = GESTURE_IMAGE_MAP.get(resolved_gestures[0])

        return image, labels, gesture_image
