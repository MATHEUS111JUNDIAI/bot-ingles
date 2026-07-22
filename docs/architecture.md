# Architecture Documentation

## Overview
Teacher Sarah (bot-ingles) é uma aplicação Flask completa para o ensino e prática de inglês com IA, servindo duas plataformas principais:
1. **Web-Chat Interativo:** Frontend em HTML/CSS (Glassmorphism) e JS conectando ao endpoint `/api/web-chat` em `src/api/routes.py`.
2. **Integração WhatsApp:** Endpoint `/bot` em `src/api/routes.py` integrado com Twilio Webhook.

---

## Core Components
- **API (routes.py):** Rotas principais e orquestração (recebe mensagens, envia para a IA e retorna o resultado).
- **Gemini Service (`src/services/gemini_service.py`):** Encapsula chamadas ao Google Gemini. Transcreve áudios do usuário, analisa gramática, gera respostas contextualizadas e extrai vocabulário via JSON Schema.
- **TTS Service (`src/services/tts_service.py`):** Converte a resposta de texto da IA para voz sintética de altíssima qualidade (Microsoft Edge-TTS).
- **File Manager (`src/utils/file_manager.py`):** Gerencia arquivos temporários em `temp/` e static audio em `static/audio/`.
- **Metrics (`src/utils/metrics.py`):** Expõe métricas Prometheus em `/metrics`.

---

## Rate Limiting
Utiliza `Flask-Limiter` em `main.py` baseado no IP para prevenir abuso sem impactar a experiência de conversação contínua.

---

## Software Engineering Diagrams (UML / PlantUML)

Todos os diagramas abaixo foram modelados em PlantUML e estão armazenados na pasta [`docs/diagrams/`](file:///c:/Users/mathe/bot-ingles/docs/diagrams/).

### 1. Diagrama de Sequência (`sequence_diagram.puml`)
Descreve a troca de mensagens em tempo real entre o Cliente (Web/WhatsApp), a Flask API e as APIs externas (Gemini, Wikipedia, Edge-TTS).

```plantuml
@startuml Sequence_Diagram_Teacher_Sarah
skinparam style strictuml
autonumber

actor "Estudante (Usuário)" as User
participant "Frontend Web / WhatsApp" as Client
participant "Flask API (routes.py)" as API
participant "Gemini Service" as Gemini
database "Google Gemini API" as GeminiAPI
participant "Wikipedia API" as Wiki
participant "TTS Service (Edge-TTS)" as TTS
participant "File Manager" as FM

User -> Client: Envia Texto ou Gravação de Áudio
Client -> API: POST /api/web-chat (ou /bot) [Payload: text / audio]

alt É mensagem de áudio
    API -> FM: Salva arquivo temporário de áudio em temp/
    API -> Gemini: enviar_audio_para_gemini(audio_path)
    Gemini -> GeminiAPI: Request Multimodal (Audio + Prompt)
    GeminiAPI --> Gemini: Resposta JSON (Transcrição + Correção + Vocabulário)
else É mensagem de texto
    API -> Gemini: enviar_texto_para_gemini(user_text)
    Gemini -> GeminiAPI: Request Text (Prompt + Struct JSON)
    GeminiAPI --> Gemini: Resposta JSON (Resposta + Correção + Vocabulário)
end

API -> Wiki: Buscar imagem da palavra chave (vocab_word)
Wiki --> API: URL da imagem / Thumbnail

API -> TTS: gerar_audio_resposta(texto_resposta)
TTS -> FM: Grava áudio MP3 da Sarah em static/audio/
TTS --> API: Caminho do arquivo de áudio

API --> Client: HTTP 200 OK (JSON: resposta, correcoes, vocab, audio_url, image_url)
Client -> User: Exibe feedback visual, card de vocabulário e reproduz áudio da Sarah

@enduml
```

---

### 2. Diagrama de Caso de Uso (`use_case_diagram.puml`)
Define as funcionalidades oferecidas aos usuários finais e administradores do sistema.

```plantuml
@startuml Use_Case_Diagram_Teacher_Sarah
left to right direction
skinparam packageStyle rectangle

actor "Estudante de Inglês" as Student
actor "Administrador / SRE" as Admin
actor "Serviço Externo (Twilio)" as Twilio

rectangle "Sistema Teacher Sarah (bot-ingles)" {
    usecase "Conversar por Texto" as UC_Text
    usecase "Praticar Pronúncia via Áudio" as UC_Audio
    usecase "Receber Feedback Gramatical" as UC_Grammar
    usecase "Estudar Cards de Vocabulário com Imagens" as UC_Vocab
    usecase "Ouvir Resposta com Voz Nativa (TTS)" as UC_TTS
    usecase "Exportar Histórico de Conversa (CSV)" as UC_Export
    usecase "Selecionar Tópicos de Gramática" as UC_Topics
    usecase "Monitorar Métricas de Desempenho (Prometheus)" as UC_Metrics
    usecase "Processar Webhook do WhatsApp" as UC_WhatsApp
}

Student --> UC_Text
Student --> UC_Audio
Student --> UC_Grammar
Student --> UC_Vocab
Student --> UC_TTS
Student --> UC_Export
Student --> UC_Topics

Twilio --> UC_WhatsApp
UC_WhatsApp ..> UC_Grammar : <<include>>
UC_WhatsApp ..> UC_TTS : <<include>>

Admin --> UC_Metrics

UC_Text ..> UC_Grammar : <<include>>
UC_Audio ..> UC_Grammar : <<include>>
UC_Grammar ..> UC_Vocab : <<include>>
UC_Grammar ..> UC_TTS : <<include>>

@enduml
```

---

### 3. Diagrama de Classe / Módulos (`class_diagram.puml`)
Apresenta a estrutura de classes, módulos e dependências do backend Python.

```plantuml
@startuml Class_Diagram_Teacher_Sarah
skinparam classAttributeIconSize 0

package "src.api" {
    class Routes {
        + web_chat() : Response
        + bot_whatsapp() : Response
        + metrics() : Response
    }
}

package "src.services" {
    class GeminiService {
        - api_key : str
        - model : str
        + enviar_mensagem(texto: str, audio_path: str) : dict
        + _construir_prompt_sistema() : str
        + _parse_json_response(raw_response: str) : dict
    }

    class TTSService {
        - voice : str
        + gerar_audio_resposta(texto: str) : str
    }
}

package "src.utils" {
    class FileManager {
        + salvar_audio_temporario(file_data) : str
        + limpar_arquivos_antigos(diretorio: str) : void
    }

    class Metrics {
        + REQUEST_COUNT : Counter
        + LATENCY_HISTOGRAM : Histogram
        + registrar_requisicao(endpoint: str, duration: float) : void
    }
}

package "External Integrations" {
    class WikipediaClient {
        + buscar_imagem_palavra(palavra: str) : str
    }
}

Routes --> GeminiService : utiliza
Routes --> TTSService : utiliza
Routes --> FileManager : utiliza
Routes --> Metrics : registra
Routes --> WikipediaClient : consulta

@enduml
```

---

### 4. Diagrama de Atividade (`activity_diagram.puml`)
Ilustra o fluxo de controle interno do pipeline de processamento do Flask.

```plantuml
@startuml Activity_Diagram_Teacher_Sarah
start
:Receber Requisição HTTP POST;

if (Validar Rate Limiting (Flask-Limiter)) then (Excedido)
    :Retornar HTTP 429 Too Many Requests;
    stop
else (Permitido)
    if (Tipo de Entrada?) then (Áudio (.webm / .mp3))
        :Salvar arquivo temporário via FileManager;
        :Enviar arquivo de áudio ao Gemini Service;
    else (Texto)
        :Extrair mensagem de texto;
        :Enviar prompt de texto ao Gemini Service;
    end if
endif

:Gemini processa e gera resposta JSON estruturada;
:Validar e realizar parse do JSON (Resposta, Correções, Vocabulário);

fork
    :Consultar Wikipedia REST API para imagem do vocab_word;
fork again
    :Gerar áudio MP3 da resposta com Edge-TTS;
end fork

:Compilar payload final de resposta HTTP JSON;
:Registrar latência e métricas em Prometheus;
:Retornar HTTP 200 OK ao cliente;
stop
@enduml
```

---

### 5. Diagrama de Componentes (`component_diagram.puml`)
Demonstra a arquitetura modular e os limites dos subsistemas.

```plantuml
@startuml Component_Diagram_Teacher_Sarah
package "Frontend Client" {
    [Web Browser UI (HTML/CSS/JS)] as WebUI
    [Twilio WhatsApp Client] as WAClient
}

package "Flask Backend Subsystem (Python 3.12)" {
    [Flask Core App (main.py)] as MainApp
    [API Routes (routes.py)] as Routes
    [Gemini Service] as GeminiSvc
    [TTS Service (Edge-TTS)] as TTSSvc
    [File Manager Utility] as FileMgr
    [Prometheus Metrics] as MetricsSvc
}

cloud "External Services & APIs" {
    [Google Gemini 3.1 API] as GeminiAPI
    [Wikipedia REST API] as WikiAPI
    [Twilio API Webhook] as TwilioAPI
}

WebUI --> Routes : HTTP POST /api/web-chat
WAClient --> TwilioAPI
TwilioAPI --> Routes : HTTP POST /bot

Routes --> GeminiSvc : Solicita IA & JSON Struct
GeminiSvc --> GeminiAPI : REST/gRPC Calls

Routes --> WikiAPI : Query Imagen Vocabulário

Routes --> TTSSvc : Converte resposta em áudio
TTSSvc --> FileMgr : Salva .mp3 em static/

Routes --> MetricsSvc : Registra métricas
@enduml
```

---

### 6. Diagrama de Estado (`state_diagram.puml`)
Representa os estados possíveis de uma transação de mensagem.

```plantuml
@startuml State_Diagram_Teacher_Sarah
[*] --> Ocioso : Inicialização da Aplicação

state Ocioso {
    [*] --> AguardandoEntrada
    AguardandoEntrada : Esperando input do usuário
}

Ocioso --> RecebendoMensagem : Usuário envia Texto ou Áudio

state RecebendoMensagem {
    [*] --> ValidandoRateLimit
    ValidandoRateLimit --> ArmazenandoTemporario : Tipo == Áudio
    ValidandoRateLimit --> EncaminhandoPayload : Tipo == Texto
}

RecebendoMensagem --> ProcessandoLLM : Payload Válido
RecebendoMensagem --> ErroRateLimit : Rate Limit Excedido (429)

state ProcessandoLLM {
    [*] --> ChamandoGemini
    ChamandoGemini --> ParsingJSON : Resposta JSON Recebida
}

ProcessandoLLM --> BuscandoRecursos : JSON Válido
ProcessandoLLM --> ErroProcessamento : Falha Gemini / JSON Inválido

state BuscandoRecursos {
    [*] --> FetchWikipediaImage
    [*] --> GenerateEdgeTTSAudio
}

BuscandoRecursos --> EnviandoResposta : Recursos Prontos

state EnviandoResposta {
    [*] --> CompilandoPayloadHTTP
    CompilandoPayloadHTTP --> RegistrandoMetricasPrometheus
}

EnviandoResposta --> Ocioso : HTTP 200 Renderizado no Cliente
ErroRateLimit --> Ocioso : Notificação exibida
ErroProcessamento --> Ocioso : Mensagem de erro amigável retornada

@enduml
```

---

### 7. Diagrama de Objeto (`object_diagram.puml`)
Representa instâncias reais de objetos de dados trocados em runtime.

```plantuml
@startuml Object_Diagram_Teacher_Sarah

object "requestPayload : WebChatRequest" as req {
    message = "I goes to the beach yesterday"
    type = "text"
    topic = "Past Simple"
}

object "geminiResponse : GeminiStructuredOutput" as resp {
    sarah_reply = "That sounds fun! Remember to use the past tense: 'I went to the beach yesterday'."
    user_transcription = "I goes to the beach yesterday"
    grammar_corrections = ["'I goes' -> 'I went' (Past Simple of 'go')"]
    study_tips = ["Practice irregular past tense verbs like go -> went, see -> saw."]
    vocab_word = "Beach"
}

object "wikiMedia : WikipediaAsset" as wiki {
    title = "Beach"
    thumbnail_url = "https://upload.wikimedia.org/.../Beach_sand.jpg"
}

object "audioOutput : TTSAudioFile" as tts {
    file_path = "/static/audio/sarah_reply_102938.mp3"
    voice_name = "en-US-AriaNeural"
}

object "finalResponsePayload : JSONResponse" as json {
    status = "success"
    sarah_text = "That sounds fun! Remember..."
    corrections = ["'I goes' -> 'I went'"]
    vocab_word = "Beach"
    image_url = "https://upload.wikimedia.org/.../Beach_sand.jpg"
    audio_url = "/static/audio/sarah_reply_102938.mp3"
}

req --> resp : processado por GeminiService
resp --> wiki : consulta vocab_word
resp --> tts : sintetiza sarah_reply
resp --> json : compila
wiki --> json : compila
tts --> json : compila

@enduml
```

---

### 8. Diagrama de Implantação (`deployment_diagram.puml`)
Mapeia os nós de hardware/software, containers e gateways em produção.

```plantuml
@startuml Deployment_Diagram_Teacher_Sarah

node "Dispositivo do Usuário" as UserDevice {
    artifact "Navegador Web (Chrome / Safari)" as Browser
    artifact "WhatsApp Mobile Client" as WhatsAppApp
}

node "Nuvem de Hospedagem (Ex: VPS / Vercel / Render)" as HostServer {
    node "Nginx / Reverse Proxy" as Proxy {
        component "SSL / TLS Termination"
    }

    node "Docker Container / Python Environment" as DockerApp {
        component "Gunicorn / WSGI Application Server" as WSGI
        component "Flask Application (main.py)" as FlaskApp
        folder "/static/audio/" as AudioStore
        folder "/temp/" as TempStore
    }
}

cloud "Google Cloud Platform" {
    node "Google Gemini API Endpoint" as GeminiCloud {
        component "Gemini 3.1 Flash Lite Model"
    }
}

cloud "Infraestrutura Twilio" {
    node "Twilio WhatsApp Gateway" as TwilioGateway
}

cloud "Serviços Públicos de Terceiros" {
    node "Wikipedia REST API" as WikiCloud
    node "Microsoft Edge-TTS Service" as EdgeTTSCloud
}

Browser --> Proxy : HTTPS (Port 443)
WhatsAppApp --> TwilioGateway : Messaging API
TwilioGateway --> Proxy : Webhook HTTP(S) POST

Proxy --> WSGI : Pass-through HTTP (Port 5000)
WSGI --> FlaskApp : Executa Rotas Python

FlaskApp --> AudioStore : Grava .mp3 gerados
FlaskApp --> TempStore : Armazena upload temporário

FlaskApp --> GeminiCloud : HTTPS REST/gRPC
FlaskApp --> WikiCloud : HTTPS GET
FlaskApp --> EdgeTTSCloud : Async WebSocket / HTTPS

@enduml
```

---

### 9. Diagrama de Tempo (`timing_diagram.puml`)
Exibe o perfil temporal de execução e latência das etapas da aplicação.

```plantuml
@startuml Timing_Diagram_Teacher_Sarah
robust "Estado do Cliente (Web / App)" as Client
robust "Flask Middleware & Rotas" as Flask
robust "Google Gemini LLM" as Gemini
robust "Wikipedia API" as Wiki
robust "Edge-TTS Engine" as TTS

@0
Client is Idle
Flask is Idle
Gemini is Idle
Wiki is Idle
TTS is Idle

@100
Client is SendingRequest
Flask is ReceivingRequest

@200
Client is WaitingResponse
Flask is CallingLLM
Gemini is ProcessingPrompt

@1500
Gemini is Idle
Flask is ProcessingJSON

@1600
Flask is ParallelFetching
Wiki is FetchingImage
TTS is SynthesizingVoice

@1800
Wiki is Idle

@2100
TTS is Idle
Flask is CompilingResponse

@2200
Flask is Idle
Client is RenderingUI

@3000
Client is Idle

highlight 100 to 2200 : Tempo total de ciclo (~2.1 segundos)
highlight 200 to 1500 : Latência Gemini LLM (~1.3s)
highlight 1600 to 2100 : Processamento Paralelo Assets (Wiki & TTS ~500ms)

@enduml
```
