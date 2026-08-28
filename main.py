import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from src.api.routes import api_bp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

app = Flask(__name__, static_folder=FRONTEND_DIR)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max payload (Anti-OOM)
CORS(app)


def get_ip():
    forwarded = request.headers.get('x-forwarded-for')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.headers.get('x-real-ip') or request.remote_addr or '127.0.0.1'


limiter = Limiter(
    get_ip,
    app=app,
    default_limits=["200 per day", "10 per minute"],
    storage_uri="memory://"
)


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Você atingiu o limite de mensagens temporário (máximo de 10 requisições por minuto)."), 429


@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify(error="O arquivo ou requisição excedeu o limite máximo permitido de 5MB."), 413


@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'microphone=(self), camera=(), geolocation=(), payment=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "media-src 'self' data: blob:; "
        "connect-src 'self' https:;"
    )
    return response


app.register_blueprint(api_bp)

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return "Not Found", 404

if __name__ == '__main__':
    print("🚀 Teacher Sarah (Web/Flask) Rodando!")
    # O metrics do Flask vai rodar na mesma porta do app Flask em /metrics
    app.run(debug=True, port=5000)
