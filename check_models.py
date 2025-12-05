import os
import time
import logging
import asyncio
import google.generativeai as genai
from openai import OpenAI
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# --- SUAS CHAVES (COLOQUE ELAS AQUI) ---
TOKEN_TELEGRAM = "8540209207:AAEPJa-MhD2cn--KwmIDHRN_AygsJ3bPiK4"
GOOGLE_API_KEY = "AIzaSyDIEhjH-lvVMQyPb_lAYbYEiVVbmhqWO9U"
OPENAI_API_KEY = "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"

# --- CONFIGURAÇÕES ---
genai.configure(api_key=GOOGLE_API_KEY)

# MUDANÇA CRUCIAL: Usando o modelo LITE para evitar bloqueios de cota
# Esse modelo gasta muito menos "créditos" do limite gratuito
model = genai.GenerativeModel('gemini-2.0-flash-lite')

openai_client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

if not os.path.exists('static'):
    os.makedirs('static')

# --- FUNÇÃO DE VOZ OPENAI ---
async def gerar_audio_openai(texto, arquivo_saida):
    loop = asyncio.get_running_loop()
    def chamar():
        try:
            # 'onyx' é voz masculina séria. Use 'alloy' para neutra ou 'nova' para feminina.
            response = openai_client.audio.speech.create(
                model="tts-1", voice="onyx", input=texto 
            )
            response.stream_to_file(arquivo_saida)
        except Exception as e:
            print(f"Erro na OpenAI: {e}")
    await loop.run_in_executor(None, chamar)

# --- FUNÇÃO COM RETRY (SAFETY NET) ---
def chamar_gemini_com_retry(prompt, arquivo_audio):
    """
    Tenta chamar o Google. Se der erro de limite (429), espera e tenta de novo.
    """
    tentativas = 0
    max_tentativas = 3
    
    while tentativas < max_tentativas:
        try:
            return model.generate_content([prompt, arquivo_audio]).text
        except Exception as e:
            erro_str = str(e)
            if "429" in erro_str:
                print(f"⚠️ Google pediu pausa (429). Esperando 10s... (Tentativa {tentativas+1})")
                time.sleep(10) # Pausa técnica
                tentativas += 1
            else:
                # Se for outro erro, não adianta esperar
                print(f"❌ Erro no Gemini: {e}")
                return "I'm having trouble thinking right now."
    
    return "System overloaded. Please wait a minute."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Lite (Rápido) Iniciado! Let's talk!")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # 1. Avisa que está ouvindo
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")

    try:
        # 2. Baixar Áudio
        file = await context.bot.get_file(update.message.voice.file_id)
        # Usamos ID único para não dar conflito de arquivo
        caminho = f"static/user_{update.update_id}.ogg"
        await file.download_to_drive(caminho)

        # 3. Enviar para Google e Processar
        # O upload é rápido, geralmente não dá erro
        arquivo_gemini = genai.upload_file(caminho)
        
        prompt = """
        You are a patient and supportive English Tutor for a beginner student.
        
        Rules:
        1. Use SIMPLE vocabulary (A2/B1 level). Speak clearly and slowly.
        2. Keep sentences short and easy to understand.
        3. If the user makes a mistake, correct it gently at the end using Portuguese for the correction explanation if necessary.
        4. IMPORTANT: Only use complex technical terms if the user explicitly asks for a "deep dive" or "technical explanation". Otherwise, keep it basic.
        """
        
        # Chama a IA (com proteção contra queda)
        loop = asyncio.get_running_loop()
        texto_resposta = await loop.run_in_executor(None, lambda: chamar_gemini_com_retry(prompt, arquivo_gemini))
        
        print(f"🤖 Resposta: {texto_resposta}")

        # 4. Gerar Áudio OpenAI (A melhor voz)
        await context.bot.send_chat_action(chat_id=chat_id, action="upload_voice")
        await gerar_audio_openai(texto_resposta, "static/resposta.mp3")

        # 5. Enviar de volta
        # Envia o áudio
        await update.message.reply_voice(voice=open("static/resposta.mp3", 'rb'))
        
        # Envia a legenda oculta (clique para ler)
        msg_legenda = f"🤖 <b>Teacher:</b> <span class='tg-spoiler'>{texto_resposta}</span>"
        await update.message.reply_text(msg_legenda, parse_mode=ParseMode.HTML)
        
        # Limpeza (Apaga o arquivo do usuário para não encher o HD)
        try:
            os.remove(caminho)
        except:
            pass

    except Exception as e:
        print(f"❌ Erro Geral: {e}")
        await update.message.reply_text("Tive um problema técnico. Tente novamente.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    print("🚀 Bot Lite Rodando! (Modelo gemini-2.0-flash-lite)")
    app.run_polling()