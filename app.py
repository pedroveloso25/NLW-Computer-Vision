from fasthtml.common import *
from core.modelos import baixar_modelo_mediapipe, carregar_modelo_customizado
from core.reconhecedor import ReconhecedorHibrido
from core.image_utils import decode_image, encode_image
# Instanciar os modelos globalmente (característica comum em FastHTML apps para evitar reload por frame)
mp_model_path = baixar_modelo_mediapipe()
clf_model = carregar_modelo_customizado()
reconhecedor = ReconhecedorHibrido(mp_model_path, clf_model)

# Inicializar app FastHTML habilitando o uso de extensões WebSocket
app, rt = fast_app(exts=['ws'])

import asyncio
from starlette.responses import FileResponse

# Servindo nossa pasta estática do front-end
@rt('/assets/{fname:path}')
def serve_assets(fname: str):
    return FileResponse(f'assets/{fname}')

@rt('/gestures/{fname:path}')
def serve_gestures(fname: str):
    return FileResponse(f'gestures/{fname}')

@rt('/')
def get():
    return Html(
        Head(
            Title("Reconhecedor de Gestos"),
            Meta(charset="UTF-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Link(rel="stylesheet", href="/assets/style.css"),
            Script(src="/assets/script.js", defer=True)
        ),
        Body(
            # Header
            Div(
                H1("Reconhecedor de Gestos"),
                P("Detecção em tempo real com MediaPipe + IA customizada", cls="subtitle"),
                cls="header"
            ),

            # Layout principal: webcam + sidebar
            Div(
                # Painel da webcam
                Div(
                    Video(id="video", autoplay=True, playsinline=True, style="display:none;"),
                    Canvas(id="canvas", width=640, height=480),
                    Div(cls="status-dot"),
                    cls="webcam-panel"
                ),

                # Sidebar dos gestos
                Div(
                    Div(
                        Div("Gesto Detectado", cls="gesture-label"),
                        Img(id="gestureImg", alt="Gesto"),
                        id="gestureCard",
                        cls="gesture-card"
                    ),
                    P("Mostre o mesmo gesto com as duas mãos", id="noMatchMsg", cls="no-match-msg"),
                    cls="gesture-sidebar"
                ),

                cls="main-container"
            ),

            # Barra de info
            Div(
                Span(id="statusDot", cls="dot active"),
                Span("WebSocket conectado", id="statusText"),
                cls="info-bar"
            )
        )
    )

import json

def process_frame_sync(encoded_str):
    # Usa a nova função de imagem isolada lá em core
    img = decode_image(encoded_str)

    if img is not None:
        # Processar com nossa class, agora nos devolve (imagem_com_landmark, lista_de_labels)
        img_processed, labels, gesture_image = reconhecedor.processar_imagem(img)
        
        # Retornamos o Base64 embutido com a metadata do texto!
        img_base64 = encode_image(img_processed)
        if img_base64:
            return json.dumps({
                "image": img_base64,
                "labels": labels,
                "gesture_image": gesture_image
            })
    
    return None

# Escutando o canal websockets na rota '/ws' nativamente pelo Starlette
async def ws(websocket):
    await websocket.accept()
    while True:
        try:
            msg = await websocket.receive_text()
            
            # Pega a string codificada do JS, e divide o header
            header, encoded = msg.split(",", 1)
            
            # Roda o processamento da imagem em uma Thread separada 
            # (pra não "congelar" a Thread principal e o server)
            out_msg = await asyncio.to_thread(process_frame_sync, encoded)
            
            if out_msg:
                # Responde para o client individual
                await websocket.send_text(out_msg)
        
        except Exception as e:
            print(f"Websocket desconectado ou erro: {e}")
            break

app.add_websocket_route('/ws', ws)

if __name__ == '__main__':
    serve()
