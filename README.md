# NLW Trilha — Reconhecimento de Gestos com Visão Computacional

> Sistema de reconhecimento de gestos em tempo real com MediaPipe + modelo scikit-learn customizado, servido via FastHTML e WebSockets.

Desenvolvido durante a **NLW (Next Level Week)** da [Rocketseat](https://rocketseat.com.br).

Veja o post sobre o projeto no [LinkedIn](https://www.linkedin.com/posts/pedro-rebou%C3%A7as-veloso_h%C3%A1-alguns-dias-finalizei-a-trilha-de-vis%C3%A3o-ugcPost-7441931003016724480-4ZCQ).

---

## Demonstração

O sistema reconhece gestos da mão pela webcam em tempo real e exibe a classificação via interface web.

Gestos suportados: personalizáveis via `gravador_dataset_landmarks.ipynb`

---

## Arquitetura

```
Webcam → MediaPipe (landmarks) → ReconhecedorHibrido → FastHTML WebSocket → Browser
```

- **MediaPipe** extrai os 21 landmarks da mão
- **ReconhecedorHibrido** classifica os landmarks com modelo scikit-learn customizado
- **FastHTML + WebSockets** serve a interface e transmite os frames processados

---

## Requisitos

- Python 3.13+
- Webcam
- [uv](https://docs.astral.sh/uv/) (recomendado) ou pip

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/pedroveloso25/NLW-Computer-Vision.git
cd NLW-Computer-Vision

# Com uv (recomendado)
uv sync

# Ou com pip
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Variáveis de ambiente

```bash
cp .env.example .env
# Edite .env e adicione sua GEMINI_API key (necessário apenas para aula02.ipynb)
```

Obtenha sua chave em: https://aistudio.google.com/app/apikey

---

## Modelos e datasets

Os modelos não estão versionados no repositório. Baixe antes de rodar:

```bash
# MediaPipe Gesture Recognizer (~8 MB)
curl -o gesture_recognizer.task \
  https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task

# EfficientDet para detecção de objetos (~4.4 MB)
curl -o efficientdet_lite0.tflite \
  https://storage.googleapis.com/mediapipe-models/object_detector/efficientdet_lite0/int8/1/efficientdet_lite0.tflite

# ImageNet classes
curl -o imagenet_classes.txt \
  https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt
```

O dataset **MNIST** é baixado automaticamente pelo torchvision ao rodar os notebooks.

O **modelo customizado de gestos** (`modelo_gestos.pkl`) está disponível na página de [Releases](../../releases) deste repositório, ou pode ser recriado do zero com os notebooks (veja abaixo).

---

## Uso

### Modo web (servidor FastHTML)

```bash
uv run app.py
# Acesse http://localhost:5001
```

### Modo local (sem servidor)

```bash
uv run python core/main.py
```

### Treinar seu próprio modelo de gestos

1. Execute `gravador_dataset_landmarks.ipynb` para capturar os gestos pela webcam — gera o `hand_landmarks_dataset.csv`
2. Execute `treinador_gestos.ipynb` para treinar e salvar `modelo_gestos.pkl`

---

## Estrutura do projeto

```
.
├── app.py                               # Servidor FastHTML principal
├── core/
│   ├── main.py                          # Entry point modo local
│   ├── reconhecedor.py                  # ReconhecedorHibrido
│   ├── modelos.py                       # Carregamento de modelos
│   ├── image_utils.py                   # Encode/decode de imagens
│   └── reconhecedor_hibrido.ipynb       # Protótipo do reconhecedor
├── assets/
│   ├── script.js                        # Frontend WebSocket
│   └── style.css                        # Estilos
├── gestures/                            # Imagens dos gestos para a UI
├── aula01.ipynb                         # Introdução ao MediaPipe
├── aula02.ipynb                         # Integração com Gemini API
├── deteccao_objetos_mediapipe.ipynb     # Detecção de objetos com MediaPipe
├── gravador_dataset_landmarks.ipynb     # Coleta de dataset de gestos
├── treinador_gestos.ipynb               # Treinamento do modelo
├── pyproject.toml
├── uv.lock
├── .python-version                      # Python 3.13
├── .env.example                         # Template de variáveis de ambiente
└── requirements.txt
```

---

## Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| Servidor | FastHTML, Uvicorn, WebSockets |
| Visão Computacional | MediaPipe, OpenCV |
| Machine Learning | scikit-learn |
| Deep Learning (notebooks) | PyTorch, TorchVision |
| IA Generativa (notebooks) | Google Gemini API |
| Gerenciamento de pacotes | uv |

---

## Créditos

Projeto desenvolvido durante a **NLW** da [Rocketseat](https://rocketseat.com.br).

Veja o post sobre o projeto no [LinkedIn](https://www.linkedin.com/posts/pedro-rebou%C3%A7as-veloso_h%C3%A1-alguns-dias-finalizei-a-trilha-de-vis%C3%A3o-ugcPost-7441931003016724480-4ZCQ).
