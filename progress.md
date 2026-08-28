# Progresso do Projeto

## Sessão Atual (Implementação de Cabeçalhos de Segurança HTTP e CSP)
- **Data:** 2026-08-28
- **Objetivo:** Adicionar cabeçalhos de segurança HTTP na Vercel (CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy) e refatorar manipuladores inline no frontend.
- **Feito:**
  - Configurados cabeçalhos de segurança em [vercel.json](file:///c:/Users/mathe/bot-ingles/vercel.json).
  - Refatorados botões de tópicos em [index.html](file:///c:/Users/mathe/bot-ingles/frontend/index.html) de `onclick` inline para atributos `data-topic`.
  - Adicionado listener de eventos unificado em [app.js](file:///c:/Users/mathe/bot-ingles/frontend/app.js) para compatibilidade estrita com Content-Security-Policy (`script-src 'self'`).
  - Atualizado [feature_list.json](file:///c:/Users/mathe/bot-ingles/feature_list.json) com a feature F03.
- **Bloqueios/Avisos:**
  - Nenhum.
- **Próximos Passos:**
  - Subir alterações para o GitHub e monitorar deploy na Vercel.

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

