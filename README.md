# 👩‍🏫 Teacher Sarah — AI-Powered Interactive English Tutor (Web Platform)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)](https://ai.google.dev/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Teacher Sarah** is a full-stack AI-powered English Learning Web Application designed for interactive speaking, listening, grammar analysis, and vocabulary acquisition.

🌐 **Live Demo:** [https://bot.matheusdev.com.br](https://bot.matheusdev.com.br)

---

## ✨ Key Features

- **🎙️ Real-Time Dual Input (Voice & Text):** Practice pronunciation using the web browser's native audio recorder (`MediaRecorder API`) or engage via text chat.
- **🧠 Multimodal LLM & Structured Output:** Powered by **Google Gemini 3.1 Flash Lite** with strict JSON Schema constraints to return structured grammar corrections, study tips, and target vocabulary.
- **🗣️ Neural Text-to-Speech (TTS):** Generates high-quality spoken audio responses using **Microsoft Edge-TTS** (`en-US-AriaNeural`), enabling authentic listening practice.
- **🖼️ Automated Vocabulary Flashcards:** Extracts key vocabulary from interactions and enriches flashcards with definitions and relevant media via the **Wikipedia REST API**.
- **📚 Guided Study Topics:** Interactive sidebar with pre-configured grammar modules (e.g., *Present Continuous*, *Past Simple*, *Conditionals*).
- **📊 Observability & Metrics:** Built-in **Prometheus** metrics endpoint (`/metrics`) tracking request counts, latencies, and system health.
- **🛡️ Resilience & Rate Limiting:** Protected by **Flask-Limiter** to enforce IP-based rate limits and prevent API abuse.
- **📥 Conversation Export:** Download complete study session history in CSV format for offline review.
- **🎨 Glassmorphism Design:** Modern, responsive, mobile-friendly UI built with vanilla HTML, CSS, and JavaScript.

---

## 🏗️ Architecture & Software Engineering

The project follows a modular, scalable architecture with clear separation of concerns:

```
┌─────────────────┐       HTTP POST        ┌──────────────────────────┐
│  Browser Client │ ─────────────────────> │  Flask API (routes.py)   │
│ (MediaRecorder) │                        └────────────┬─────────────┘
└─────────────────┘                                     │
                                   ┌────────────────────┼────────────────────┐
                                   ▼                    ▼                    ▼
                        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
                        │  Gemini Service  │  │   TTS Service    │  │ Wikipedia Client │
                        │ (JSON Schema LLM)│  │    (Edge-TTS)    │  │   (Media Assets) │
                        └──────────────────┘  └──────────────────┘  └──────────────────┘
```

Detailed UML software architecture diagrams are available in [`docs/architecture.md`](docs/architecture.md) and [`docs/diagrams/`](docs/diagrams/):
- 📐 **Sequence Diagram:** Full HTTP execution cycle and parallel asset resolution.
- 📐 **Component & Class Diagrams:** Modular backend Python structure.
- 📐 **Timing Diagram:** Latency profiling (~2.1s total end-to-end response time).
- 📐 **Deployment & State Diagrams:** Production deployment and transaction states.

---

## 🛠️ Tech Stack

| Domain | Technology |
| :--- | :--- |
| **Backend Framework** | Python 3.12, Flask, Gunicorn |
| **Frontend UI** | HTML5, CSS3 (Glassmorphism), Vanilla JavaScript |
| **Artificial Intelligence** | Google Gemini 3.1 Flash Lite API (Multimodal / JSON Output) |
| **Voice Synthesis** | Microsoft Edge-TTS (`edge-tts`) |
| **Third-Party APIs** | Wikipedia REST API |
| **Observability** | Prometheus (`prometheus-client`), Flask-Limiter |
| **Testing & Quality** | Pytest, Flake8 |

---

## 📦 Getting Started

### Prerequisites
- Python 3.12+
- Google Gemini API Key ([Get a key here](https://aistudio.google.com/))

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MATHEUS111JUNDIAI/bot-ingles.git
   cd bot-ingles
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

5. **Run the Application:**
   ```bash
   python main.py
   ```

6. **Access in Browser:**
   Navigate to `http://127.0.0.1:5000`

---

## 🧪 Testing & Code Quality

Run automated linting and tests using the project harness script:

```bash
# Windows
.\init.bat

# Linux / macOS
flake8 src tests
pytest
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.