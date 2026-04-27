const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const gestureImg = document.getElementById('gestureImg');
const gestureCard = document.getElementById('gestureCard');
const noMatchMsg = document.getElementById('noMatchMsg');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// Conectar no backend via web socket
const wsProto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(wsProto + window.location.host + '/ws');

// Pedir permissão da câmera
navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 }, audio: false })
    .then(stream => { 
        video.srcObject = stream; 
    })
    .catch(err => alert("Erro ao acessar a câmera: " + err));

// Função que envia 1 frame para o Python processar
function sendFrame() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = 480; 
        tempCanvas.height = 360;
        const tempCtx = tempCanvas.getContext('2d');
        tempCtx.drawImage(video, 0, 0, tempCanvas.width, tempCanvas.height);
        
        const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.5);
        ws.send(dataUrl);
    } else {
        setTimeout(sendFrame, 50);
    }
}

// WebSocket lifecycle
ws.onopen = () => {
    statusDot.classList.add('active');
    statusText.textContent = 'WebSocket conectado';
    sendFrame();
};

ws.onclose = () => {
    statusDot.classList.remove('active');
    statusText.textContent = 'Desconectado';
};

// Cache da última imagem mostrada para evitar flicker
let lastGestureImage = null;

ws.onmessage = (event) => {
    try {
        const payload = JSON.parse(event.data);
        const img = new Image();
        
        img.onload = () => {
            // 1. Desenha o frame processado
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            
            // 2. Desenha os rótulos da IA
            if (payload.labels) {
                const scaleX = canvas.width / 480; 
                const scaleY = canvas.height / 360;

                payload.labels.forEach((label) => {
                    // Sombra para legibilidade
                    ctx.save();
                    ctx.shadowColor = 'rgba(0,0,0,0.7)';
                    ctx.shadowBlur = 4;
                    ctx.fillStyle = label.color;
                    ctx.font = "bold 22px 'Inter', Arial"; 
                    ctx.fillText(label.text, label.x * scaleX, label.y * scaleY);
                    ctx.restore();
                });
            }
            
            // 3. Mostrar/ocultar o card do gesto na sidebar
            if (payload.gesture_image) {
                if (payload.gesture_image !== lastGestureImage) {
                    gestureImg.src = '/gestures/' + payload.gesture_image;
                    lastGestureImage = payload.gesture_image;
                }
                gestureCard.classList.add('visible', 'matched');
                noMatchMsg.style.display = 'none';
            } else {
                gestureCard.classList.remove('visible', 'matched');
                noMatchMsg.style.display = 'block';
                lastGestureImage = null;
            }

            requestAnimationFrame(sendFrame);
        };
        
        img.src = payload.image;
        
    } catch(err) {
        console.error("Erro ao renderizar resposta:", err);
    }
};
