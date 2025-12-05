# 🤖 AI English Teacher Bot

Este projeto é um protótipo de um Chatbot que ensina inglês através de conversas de áudio via Telegram.

O sistema atua como um professor particular, ouvindo a pronúncia do aluno, transcrevendo o áudio, corrigindo erros gramaticais e mantendo uma conversa natural e fluida com voz nativa.

## 🚀 Funcionalidades

- **Conversação por Voz:** O aluno envia áudios e recebe respostas em áudio.
- **Correção Inteligente:** A IA analisa a gramática e corrige erros sutilmente ao final da fala.
- **Memória de Longo Prazo:** O bot lembra das conversas anteriores (utilizando MySQL).
- **Voz Natural:** Utiliza a API da OpenAI para gerar uma voz fluida e calma (Teacher Sarah).
- **Transcrição e Legenda:** Retorna o texto do que o aluno disse e a resposta do professor (com spoiler para treino de listening).

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12
- **Interface:** Telegram Bot API (`python-telegram-bot`)
- **Cérebro (LLM):** Google Gemini 2.0 Flash Lite (via `google-generativeai`)
- **Voz (TTS):** OpenAI Audio API (`tts-1`)
- **Banco de Dados:** MySQL (`mysql-connector-python`)
- **Segurança:** Variáveis de ambiente (`python-dotenv`)

## 📦 Como rodar este projeto

### Pré-requisitos
- Python instalado
- MySQL Server rodando
- Conta no Telegram

### Instalação

1. Clone o repositório:
```bash
git clone [https://github.com/SEU_USUARIO/bot-ingles.git](https://github.com/MATHEUS111JUNDIAI/bot-ingles.git)