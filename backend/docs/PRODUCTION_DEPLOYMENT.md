# Guia de producao do backend

Este guia consolida o deploy e a operacao do backend Django no Render, usando Aiven/MySQL, Cloudinary, Firebase e SMTP.

## URLs principais

Substitua `https://SEU_BACKEND` pela URL real do Render.

```text
Admin Django:        https://SEU_BACKEND/admin/
Health check:        https://SEU_BACKEND/health/
Swagger/OpenAPI:     https://SEU_BACKEND/api/docs/
Schema OpenAPI:      https://SEU_BACKEND/api/schema/
API base:            https://SEU_BACKEND/api/
Auth login:          https://SEU_BACKEND/auth/login/
Auth register:       https://SEU_BACKEND/auth/register/
Dashboard report:    https://SEU_BACKEND/api/reports/dashboard/
Segments:            https://SEU_BACKEND/api/segments/
```

## Deploy no Render

Configuracao esperada:

```yaml
runtime: python
rootDir: .
buildCommand: bash backend/build.sh
startCommand: cd backend && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
healthCheckPath: /health/
```

O `backend/build.sh` executa:

1. instala dependencias;
2. roda `python manage.py migrate`;
3. cria/atualiza admin se as variaveis `DJANGO_SUPERUSER_*` existirem;
4. roda `python manage.py collectstatic --noinput`.

O `render.yaml` tambem declara:

- `projeto-miranda-redis`: broker/cache Redis;
- `projeto-miranda-celery-worker`: processa envios push e retentativas;
- `projeto-miranda-celery-beat`: agenda rotinas periodicas de retry, limpeza e marcacao de entregas antigas.

O web service nao deve executar envio massivo diretamente quando `PUSH_DISPATCH_ASYNC=true`; ele cria os logs e enfileira a tarefa para o worker.

## Variaveis obrigatorias no Render

### Django e seguranca

```text
SECRET_KEY
DEBUG=false
ALLOWED_HOSTS=seu-backend.onrender.com
SECURE_SSL_REDIRECT=true
SESSION_COOKIE_SECURE=true
CSRF_COOKIE_SECURE=true
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_AGE=28800
SESSION_EXPIRE_AT_BROWSER_CLOSE=true
MANAGER_TOKEN_TTL_SECONDS=28800
MANAGER_TOKEN_ROTATE_ON_LOGIN=true
```

### Banco Aiven/MySQL

```text
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DB_CA_CERT
DB_SSL_REQUIRED=true
```

Alternativa aceita:

```text
DATABASE_URL=mysql://USER:PASSWORD@HOST:PORT/DB?ssl-mode=REQUIRED
```

### CORS/CSRF e frontend

```text
FRONTEND_URL=https://SEU_FRONTEND
CORS_ALLOW_ALL_ORIGINS=false
CORS_ALLOWED_ORIGINS=https://SEU_FRONTEND
CSRF_TRUSTED_ORIGINS=https://SEU_FRONTEND,https://SEU_BACKEND
```

### Cloudinary

```text
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
CLOUDINARY_MEDIA_FOLDER=nexa
```

### Firebase push notification

```text
PUSH_DISPATCH_ON_PUBLISH=true
PUSH_DISPATCH_ASYNC=true
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID
FIREBASE_CLIENT_EMAIL
FIREBASE_PRIVATE_KEY
```

`FIREBASE_PRIVATE_KEY` deve manter as quebras como `\n`:

```text
"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

### Redis/Celery

```text
REDIS_URL
CELERY_BROKER_URL=redis://...   # opcional se REDIS_URL estiver definido
CELERY_RESULT_BACKEND=redis://... # opcional se REDIS_URL estiver definido
```

Todos os servicos `web`, `celery-worker` e `celery-beat` precisam compartilhar `SECRET_KEY`, credenciais do banco, Redis, Firebase e Cloudinary. No blueprint, `REDIS_URL` vem do servico Redis; os demais segredos marcados como `sync: false` devem ser preenchidos no Render.

### SMTP/e-mail

```text
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL
```

### Admin inicial

Opcional, usado no build:

```text
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

Se essas variaveis existirem, o build executa `python manage.py upsert_admin`.

## Checklist antes do deploy

- Todas as variaveis obrigatorias foram cadastradas no Render.
- `DEBUG=false`.
- `CORS_ALLOW_ALL_ORIGINS=false`.
- Banco Aiven aceita conexao do Render com SSL.
- Cloudinary esta com credenciais validas.
- Firebase esta com service account valida.
- `FIREBASE_ENABLED=true` somente quando as credenciais estiverem certas.
- Redis esta criado e `REDIS_URL` aparece nos servicos web, worker e beat.
- `PUSH_DISPATCH_ASYNC=true` somente quando worker e Redis estiverem ativos.
- `SECRET_KEY` e credenciais de banco sao iguais entre web, worker e beat.
- SMTP foi configurado se reset de senha por e-mail for necessario.
- Backup automatico do Aiven foi conferido.

## Comandos uteis em producao

Rodar migrations manualmente:

```bash
cd backend
python manage.py migrate
```

Criar/atualizar admin via env:

```bash
cd backend
python manage.py upsert_admin
```

Checar configuracao Django:

```bash
cd backend
python manage.py check
```

Checar configuracao de producao:

```bash
cd backend
python manage.py check --deploy
```

Rodar worker Celery localmente:

```bash
cd backend
celery -A core worker --loglevel=info
```

Rodar scheduler Celery Beat localmente:

```bash
cd backend
celery -A core beat --loglevel=info
```

Validar variaveis locais sem imprimir segredos:

```bash
cd backend
python scripts/validate_env.py
```

Testar conexao com banco:

```bash
cd backend
python scripts/test_db_connection.py
```

## Checklist pos-deploy

1. Abrir `/health/` e confirmar resposta `status=healthy`.
2. Abrir `/api/docs/` e confirmar Swagger carregando.
3. Acessar `/admin/` com o admin inicial.
4. Chamar `/api/reports/dashboard/` autenticado como admin.
5. Criar ou confirmar uma instituicao.
6. Criar ou atualizar identidade visual.
7. Criar um segmento em `/api/segments/`, se a prefeitura/camara usar envio segmentado.
8. Criar comunicado rascunho.
9. Publicar comunicado.
10. Confirmar que logs de entrega foram criados.
11. Confirmar que `/api/audit-logs/` registrou a acao.
12. Testar upload de PDF/imagem em comunicado.
13. Confirmar URL do anexo no Cloudinary.
14. Registrar um token em `/api/push-devices/`.
15. Publicar comunicado e verificar `push_dispatch.queued=true` quando `PUSH_DISPATCH_ASYNC=true`.
16. Conferir logs do `projeto-miranda-celery-worker` e confirmar envio ou falha registrada.
17. Se houver token real, confirmar `sent > 0` e recebimento no app/PWA.
18. Testar reset de senha se SMTP estiver configurado.

## Teste rapido de API

Login:

```http
POST /auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "SENHA"
}
```

Criar dispositivo push:

```http
POST /api/push-devices/
Content-Type: application/json

{
  "token": "TOKEN_FIREBASE",
  "platform": "web"
}
```

Criar segmento:

```http
POST /api/segments/
Authorization: Bearer TOKEN_ADMIN
Content-Type: application/json

{
  "name": "Bairro Centro",
  "slug": "bairro-centro",
  "description": "Moradores do centro",
  "users": [1],
  "push_devices": [2]
}
```

Criar comunicado segmentado:

```http
POST /api/announcements/
Authorization: Bearer TOKEN_ADMIN
Content-Type: application/json

{
  "title": "Comunicado segmentado",
  "content": "Mensagem oficial.",
  "status": "draft",
  "segments": [1]
}
```

Se `segments` estiver vazio ou ausente, o comunicado sera enviado para todos os dispositivos ativos.

Publicar comunicado:

```http
POST /api/announcements/{id}/publish/
Authorization: Bearer TOKEN_ADMIN
```

Resposta esperada quando Firebase esta configurado:

```json
{
  "push_dispatch": {
    "configured": true,
    "sent": 1,
    "failed": 0,
    "pending": 0,
    "skipped": false
  }
}
```

Resposta esperada quando o envio assincrono esta ativo:

```json
{
  "push_dispatch": {
    "configured": true,
    "sent": 0,
    "failed": 0,
    "pending": 1,
    "queued": true,
    "skipped": false
  }
}
```

## Operacao continua

- Revisar logs do Render apos cada deploy.
- Conferir backup Aiven semanalmente.
- Testar restore mensalmente conforme `backend/docs/BACKUP_RESTORE.md`.
- Revisar usuarios administradores periodicamente em `/api/managers/`.
- Gestores recebem token rotacionado no login e expirado conforme `MANAGER_TOKEN_TTL_SECONDS`.
- Revisar solicitacoes LGPD em `/api/privacy-requests/`.
- Revisar auditoria em `/api/audit-logs/`.

## Documentos relacionados

```text
backend/docs/BACKUP_RESTORE.md
backend/docs/AIVEN_SSL_TROUBLESHOOTING.md
backend/README.md
render.yaml
```
