import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Carrega a chave
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ ERRO: Chave não encontrada no .env")
    exit()

print(f"🔑 Usando chave final: ...{api_key[-5:]}")

# 2. Configura
genai.configure(api_key=api_key)

print("📡 Perguntando ao Google quais modelos você tem acesso...")

try:
    # 3. Lista os modelos
    modelos = genai.list_models()
    encontrou = False
    
    print("\n✅ MODELOS DISPONÍVEIS PARA VOCÊ:")
    for m in modelos:
        if 'generateContent' in m.supported_generation_methods:
            print(f" - {m.name}")
            encontrou = True
            
    if not encontrou:
        print("\n⚠️ Nenhum modelo de texto encontrado. Sua chave pode estar bloqueada ou ser de outro serviço (Vertex AI).")

except Exception as e:
    print(f"\n❌ ERRO DE CONEXÃO: {e}")