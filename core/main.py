import cv2
from modelos import baixar_modelo_mediapipe, carregar_modelo_customizado
from reconhecedor import ReconhecedorHibrido

def main():
    print("Iniciando o sistema de reconhecimento...")

    # 1. Carregar os modelos (MediaPipe e Scikit-Learn customizado)
    mp_model_path = baixar_modelo_mediapipe()
    clf_model = carregar_modelo_customizado()

    # 2. Inicializar o reconhecedor (isso já carrega os utilitários internamente)
    reconhecedor = ReconhecedorHibrido(mp_model_path, clf_model)
    print("Reconhecedor inicializado com sucesso!")

    # 3. Inicializar a Webcam (0 é a câmera padrão)
    cap = cv2.VideoCapture(0)

    print("Abrindo a Webcam... Pressione a tecla 'q' na janela de vídeo para sair.")

    try:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Captura da webcam falhou ou arquivo terminou. Saindo...")
                break

            # 4. Extração da função processar_imagem que trata um único frame
            # Recebe a imagem input, retorna a imagem output anotada com nosso reconhecedor híbrido
            processed_image = reconhecedor.processar_imagem(image)

            # Mostrando o frame com os resultados 
            cv2.imshow('Reconhecimento de Gestos Híbrido', processed_image)
            
            # Espera o clique da tecla 'q' para sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        print("Script interrompido pelo usuário.")
    finally:
        # Liberar recursos quando finalizado ou abortado
        cap.release()
        cv2.destroyAllWindows()
        print("Webcam liberada. Programa encerrado!")

if __name__ == '__main__':
    main()
