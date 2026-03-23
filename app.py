import os
import requests
import asyncio
import edge_tts
import google.generativeai as genai
from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configuração do Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')
app = Flask(__name__)

# Pasta para salvar os áudios temporários
UPLOAD_FOLDER = 'static'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# FUNÇÕES AUXILIARES

async def gerar_audio_resposta(texto, arquivo_saida):
    """Converte texto em áudio usando Edge-TTS (Vozes Microsoft)"""
    # Vozes boas: 'en-US-ChristopherNeural', 'en-US-AriaNeural', 'en-GB-SoniaNeural'
    communicate = edge_tts.Communicate(texto, "en-US-ChristopherNeural")
    await communicate.save(arquivo_saida)

def processar_com_gemini(caminho_audio_usuario):
    """Envia o áudio para o Gemini e recebe a resposta em texto"""
    print("Enviando áudio para o Gemini...")
    
    # Upload do arquivo para a infra do Google
    arquivo_gemini = genai.upload_file(caminho_audio_usuario)
    
    prompt = """
    You are a friendly English Tutor. The user is practicing English via WhatsApp audio.
    1. Listen to the user's audio.
    2. Respond naturally to the conversation in English.
    3. Keep your response concise (maximum 2 sentences).
    4. If the user makes a significant grammar mistake, gently correct it after your response.
    """
    
    response = model.generate_content([prompt, arquivo_gemini])
    return response.text

# ROTAS DO SERVIDOR

@app.route('/bot', methods=['POST'])
def bot():
    """Recebe a mensagem do WhatsApp (Twilio)"""
    msg_recebida = request.values.get('Body', '').lower()
    media_url = request.values.get('MediaUrl0') # URL do áudio se houver
    remetente = request.values.get('From')
    
    resp = MessagingResponse()
    msg = resp.message()

    # 1. Se o usuário mandou áudio
    if media_url:
        print(f"Áudio recebido de {remetente}")
        
        # Baixar o áudio do WhatsApp (Twilio)
        caminho_input = os.path.join(UPLOAD_FOLDER, 'input.ogg') # WhatsApp usa OGG
        with open(caminho_input, 'wb') as f:
            f.write(requests.get(media_url).content)
            
        # Processar com Gemini
        resposta_texto = processar_com_gemini(caminho_input)
        print(f"Gemini respondeu: {resposta_texto}")
        
        # Gerar áudio da resposta (TTS)
        caminho_output = os.path.join(UPLOAD_FOLDER, 'resposta.mp3')
        asyncio.run(gerar_audio_resposta(resposta_texto, caminho_output))
        
        # Enviar de volta para o WhatsApp
        # O Twilio precisa de uma URL pública para acessar o MP3 que criamos
        # O 'request.host_url' pega a URL do Ngrok automaticamente
        url_audio_resposta = f"{request.host_url}static/resposta.mp3"
        
        msg.body(f"🤖 {resposta_texto}") # Manda o texto também (opcional)
        #msg.media(url_audio_resposta)   # Manda o áudio
            
    # 2. Se for só texto
    else:
        msg.body("Mande um áudio para treinarmos sua pronúncia! 🎤")

    return str(resp)

# Rota para servir os arquivos de áudio (para o Twilio conseguir baixar)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # Roda na porta 5000
    app.run(debug=True, port=5000)