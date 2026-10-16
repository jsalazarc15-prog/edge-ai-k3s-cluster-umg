from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

app = FastAPI(title="Asistente Edge AI - Air-Gapped Cluster")

OLLAMA_API_URL = "http://ollama-service.default.svc.cluster.local:11434/api/generate"
MODEL_NAME = "qwen2:0.5b"

HTML_INTERFACE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asistente Edge AI (Sin Conexión)</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: system-ui, sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }
        header { background-color: #161b22; padding: 15px 25px; border-bottom: 1px solid #30363d; display: flex; justify-content: space-between; align-items: center; }
        .badge { background-color: #238636; color: #fff; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        #chat-box { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
        .msg { max-width: 75%; padding: 12px 16px; border-radius: 8px; line-height: 1.5; white-space: pre-wrap; }
        .user { background-color: #1f6feb; color: white; align-self: flex-end; }
        .bot { background-color: #21262d; border: 1px solid #30363d; align-self: flex-start; }
        footer { padding: 15px 25px; background-color: #161b22; border-top: 1px solid #30363d; display: flex; gap: 10px; }
        input { flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #30363d; background-color: #0d1117; color: white; outline: none; }
        button { background-color: #238636; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #2ea043; }
    </style>
</head>
<body>
    <header>
        <div><strong>Asistente Edge AI</strong> — Clúster K3s Alta Disponibilidad</div>
        <span class="badge">AIR-GAPPED / MODELO: QWEN2:0.5B</span>
    </header>
    <div id="chat-box">
        <div class="msg bot">Sistema activo en red local privada (192.168.1.0/24). ¿En qué puedo ayudarte hoy?</div>
    </div>
    <footer>
        <input type="text" id="prompt" placeholder="Escribe tu consulta local aquí..." onkeypress="if(event.key==='Enter') enviar()">
        <button onclick="enviar()">Enviar</button>
    </footer>
    <script>
        async function enviar() {
            const input = document.getElementById('prompt');
            const box = document.getElementById('chat-box');
            const texto = input.value.trim();
            if (!texto) return;
            
            box.innerHTML += `<div class="msg user">${texto}</div>`;
            input.value = '';
            
            // Mensaje temporal de carga
            const loadingId = 'loading-' + Date.now();
            box.innerHTML += `<div id="${loadingId}" class="msg bot">Procesando inferencia en nodo Worker (Lenovo)...</div>`;
            box.scrollTop = box.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: texto})
                });
                const data = await res.json();
                
                // Remover mensaje de carga y poner la respuesta real
                document.getElementById(loadingId).remove();
                box.innerHTML += `<div class="msg bot">${data.response}</div>`;
            } catch (e) {
                document.getElementById(loadingId).remove();
                box.innerHTML += `<div class="msg bot" style="color: #f85149;">Error de comunicación con el motor de IA.</div>`;
            }
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_INTERFACE

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(OLLAMA_API_URL, json=payload)
        result = resp.json()
    return JSONResponse({"response": result.get("response", "Error en nodo de inferencia.")})
