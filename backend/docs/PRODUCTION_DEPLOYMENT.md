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
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID
FIREBASE_CLIENT_EMAIL
FIREBASE_PRIVATE_KEY
```

`FIREBASE_PRIVATE_KEY` deve manter as quebras como `\n`:

```text
"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

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
15. Publicar comunicado e verificar `push_dispatch.configured=true`.
16. Se houver token real, confirmar `sent > 0` e recebimento no app/PWA.
17. Testar reset de senha se SMTP estiver configurado.

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

## Operacao continua

- Revisar logs do Render apos cada deploy.
- Conferir backup Aiven semanalmente.
- Testar restore mensalmente conforme `backend/docs/BACKUP_RESTORE.md`.
- Revisar usuarios administradores periodicamente em `/api/managers/`.
- Revisar solicitacoes LGPD em `/api/privacy-requests/`.
- Revisar auditoria em `/api/audit-logs/`.

## Documentos relacionados

```text
backend/docs/BACKUP_RESTORE.md
backend/docs/AIVEN_SSL_TROUBLESHOOTING.md
backend/README.md
render.yaml
```
