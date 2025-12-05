import os
import time
import json
import logging
import mysql.connector
import asyncio
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Chaves de API
TOKEN_TELEGRAM = "8540209207:AAEPJa-MhD2cn--KwmIDHRN_AygsJ3bPiK4"
GOOGLE_API_KEY = "AIzaSyAC_zqrGo-GmtkjTgQgyxCDYrqMiWFDLG4"
OPENAI_API_KEY = "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"

# My SQL Config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '', 
    'database': 'bot_ingles'
}

# Setup
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')
openai_client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
if not os.path.exists('static'): os.makedirs('static')

# Banco De Dados
def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"Erro MySQL: {e}")
        return None

def salvar_no_banco(user_text, bot_text):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        sql = "INSERT INTO conversas (data, user_text, bot_text) VALUES (%s, %s, %s)"
        cursor.execute(sql, (datetime.now(), user_text, bot_text))
        conn.commit()
        conn.close()

def ler_ultimas_conversas(limite=3):
    conn = get_db_connection()
    dados = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_text, bot_text FROM conversas ORDER BY id DESC LIMIT %s", (limite,))
        dados = cursor.fetchall()
        conn.close()
    return dados

# IA
async def gerar_audio_openai(texto, arquivo_saida):
    loop = asyncio.get_running_loop()
    def chamar():
        try:
            # Caractristicas da voz:
            # 1. voice="shimmer": É a voz mais calma e doce da OpenAI.
            # 2. speed=0.85: Reduz a velocidade em 15%. Fica pausado e claro.
            response = openai_client.audio.speech.create(
                model="tts-1", 
                voice="shimmer", 
                input=texto,
                speed=0.85        # O segredo da velocidade (0.25 a 4.0)
            )
            response.stream_to_file(arquivo_saida)
        except Exception as e:
            print(f"Erro OpenAI: {e}")
    await loop.run_in_executor(None, chamar)

def passo_1_transcrever(arquivo_audio):
    """
    Passo 1: Apenas ouve e escreve. Sem contexto, sem personalidade.
    Isso evita que ele invente respostas na transcrição.
    """
    prompt = """
    You are a professional Transcriber tool.
    Task: Transcribe the audio file exactly word for word.
    Rules: 
    - Do NOT reply to the content.
    - Do NOT add labels like "Speaker:" or "Transcription:".
    - Just output the raw text.
    """
    try:
        response = model.generate_content([prompt, arquivo_audio])
        return response.text.strip()
    except Exception as e:
        print(f"Erro Transcrição: {e}")
        return "(Audio error)"

def passo_2_responder(texto_usuario):
    """
    Passo 2: Pega o texto limpo e gera a resposta da Sarah.
    """
    # Busca memória
    ultimas = ler_ultimas_conversas(3)
    historico = ""
    if ultimas:
        for u, b in reversed(ultimas):
            historico += f"Student: {u}\nSarah: {b}\n"
    
    prompt = f"""
    HISTORY CONTEXT:
    {historico}
    
    CURRENT INPUT:
    Student: "{texto_usuario}"
    
    YOUR ROLE:
    You are 'Sarah', a friendly English Teacher (A2/B1 level).
    
    TASK:
    Respond to the Student's input naturally.
    - Keep it concise (max 2 sentences).
    - If the student made a grammar mistake, correct it gently at the end.
    - Do NOT format as JSON. Just give me the plain text response.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Erro Resposta: {e}")
        return "I'm having trouble thinking right now."

# BOT HANDLERS 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Teacher Sarah (Fixed Version) is ready!")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await context.bot.send_chat_action(chat_id=chat_id, action="record_voice")

    try:
        # 1. Baixar
        file = await context.bot.get_file(update.message.voice.file_id)
        caminho = f"static/user_{update.update_id}.ogg"
        await file.download_to_drive(caminho)
        arquivo_gemini = genai.upload_file(caminho)
        
        # 2. PASSO 1: TRANSCRIÇÃO PURA (Executada no ThreadPool para não travar)
        loop = asyncio.get_running_loop()
        transcricao = await loop.run_in_executor(None, lambda: passo_1_transcrever(arquivo_gemini))
        
        print(f"🗣️ Texto detectado: {transcricao}")

        # Se a transcrição vier vazia ou com erro
        if not transcricao or transcricao == "(Audio error)":
            await update.message.reply_text("I couldn't hear you clearly.")
            return

        # 3. PASSO 2: CÉREBRO DA SARAH
        resposta = await loop.run_in_executor(None, lambda: passo_2_responder(transcricao))
        
        print(f"🤖 Sarah respondeu: {resposta}")
        
        # Salva no Banco
        salvar_no_banco(transcricao, resposta)

        # 4. Gera Áudio e Envia
        await context.bot.send_chat_action(chat_id=chat_id, action="upload_voice")
        await gerar_audio_openai(resposta, "static/resposta.mp3")
        
        await update.message.reply_voice(voice=open("static/resposta.mp3", 'rb'))
        
        msg_legenda = (
            f"🗣️ <i>{transcricao}</i>\n\n"
            f"🤖 <b>Sarah:</b> <span class='tg-spoiler'>{resposta}</span>"
        )
        await update.message.reply_text(msg_legenda, parse_mode=ParseMode.HTML)
        
        try: os.remove(caminho)
        except: pass

    except Exception as e:
        print(f"❌ Erro Crítico: {e}")
        await update.message.reply_text("Technical error. Try again.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    print("🚀 Teacher Sarah (Estratégia 2 Passos) Rodando!")
    app.run_polling()