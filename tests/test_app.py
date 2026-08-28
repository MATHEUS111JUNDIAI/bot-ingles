import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_metrics_route(client):
    """Testa se a rota /metrics retorna HTTP 200"""
    response = client.get('/metrics')
    assert response.status_code == 200


def test_index_route(client):
    """Testa se a rota principal (frontend) retorna HTTP 200"""
    response = client.get('/')
    assert response.status_code == 200


def test_security_headers(client):
    """Testa se os cabeçalhos de segurança estão presentes nas respostas"""
    response = client.get('/')
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'microphone=(self)' in response.headers.get('Permissions-Policy', '')
    assert "default-src 'self'" in response.headers.get('Content-Security-Policy', '')


def test_audio_size_limit_413(client):
    """Testa se arquivos de áudio maiores que 5MB retornam HTTP 413"""
    import io
    oversized_data = b"0" * (5 * 1024 * 1024 + 1024)  # 5MB + 1KB
    response = client.post(
        '/api/web-chat',
        data={'audio': (io.BytesIO(oversized_data), 'test_audio.webm')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 413
    assert "5MB" in response.get_json().get("error", "")
