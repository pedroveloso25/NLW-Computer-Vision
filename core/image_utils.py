import base64
import cv2
import numpy as np

def decode_image(encoded_str: str):
    """Decodifica de Base64 de volta para Imagem numpy do OpenCV."""
    img_bytes = base64.b64decode(encoded_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

from typing import Optional

def encode_image(img_processed) -> Optional[str]:
    """Recodifica a imagem processada para o formato JPEG e a converte em Base64 para envio."""
    ret, buffer = cv2.imencode('.jpg', img_processed)
    if ret:
        encoded_ret = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_ret}"
    return None
