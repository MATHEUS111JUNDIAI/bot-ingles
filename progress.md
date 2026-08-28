# Progresso do Projeto

## Sessão Atual (Implementação de Segurança: Headers CSP, Rate Limiting e Anti-OOM)
- **Data:** 2026-08-28
- **Objetivo:** Implementar cabeçalhos de segurança HTTP na Vercel e Flask (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy), Rate Limiting no backend da IA (10 req/min) e limite de áudio de 5MB (Anti-OOM).
- **Feito:**
  - Configurados cabeçalhos de segurança em [vercel.json](file:///c:/Users/mathe/bot-ingles/vercel.json) e no hook `@app.after_request` de [main.py](file:///c:/Users/mathe/bot-ingles/main.py).
  - Refatorados botões de tópicos em [index.html](file:///c:/Users/mathe/bot-ingles/frontend/index.html) e [app.js](file:///c:/Users/mathe/bot-ingles/frontend/app.js) para compatibilidade com CSP estrito.
  - Implementado `MAX_CONTENT_LENGTH = 5MB` e handler HTTP 413 em [main.py](file:///c:/Users/mathe/bot-ingles/main.py) e validação de tamanho de áudio em [routes.py](file:///c:/Users/mathe/bot-ingles/src/api/routes.py).
  - Refinado extrator de IP (`x-forwarded-for`) e handler HTTP 429 para rate limiting.
  - Adicionados testes automatizados em [test_app.py](file:///c:/Users/mathe/bot-ingles/tests/test_app.py) para headers e erro 413.
  - Atualizado [feature_list.json](file:///c:/Users/mathe/bot-ingles/feature_list.json) com as features F03 e F04.
- **Bloqueios/Avisos:**
  - Nenhum.
- **Próximos Passos:**
  - Enviar alterações para o GitHub.

## Sessão Anterior (Reformulação do README.md para Apresentação de Portfólio)
- **Data:** 2026-07-31
- **Objetivo:** Reescrever o README.md para apresentar a Teacher Sarah como uma Plataforma Web completa com IA Multimodal, TTS, Observabilidade (Prometheus) e documentação UML.
- **Feito:**
  - Reformulado [README.md](file:///c:/Users/mathe/bot-ingles/README.md) removendo referências legadas de "bot de Telegram".
  - Adicionadas badges de tecnologias (Python 3.12, Flask, Gemini, Prometheus).
  - Incluída visão geral da arquitetura, diagrama ASCII e referências aos diagramas PlantUML em `docs/architecture.md`.
  - Verificação com `.\init.bat` (flake8 + pytest) aprovada com sucesso.
- **Bloqueios/Avisos:**
  - Opcional: Atualizar nome do repositório no GitHub de `bot-ingles` para `teacher-sarah-web` ou similar.
- **Próximos Passos:**
  - Ajustar o currículo/LinkedIn para alinhar com o novo README e a arquitetura Web do repositório.

