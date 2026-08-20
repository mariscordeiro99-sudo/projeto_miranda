# Backup e restauracao do backend

Este documento define o procedimento operacional para proteger dados do banco Aiven/MySQL e arquivos armazenados no Cloudinary.

## Escopo

Dados cobertos:

- Banco de dados relacional: usuarios, perfis, comunicados, anexos, dispositivos push, logs de entrega, auditoria e solicitacoes LGPD.
- Arquivos de midia: logos, brasoes, fotos de perfil e anexos enviados para Cloudinary.
- Variaveis de ambiente: credenciais do banco, Cloudinary, Firebase, SMTP e chaves Django.

Dados fora do backup do banco:

- Arquivos binarios ficam no Cloudinary.
- Variaveis do Render devem ser exportadas/documentadas separadamente, sem commitar segredos.

## Politica minima recomendada

- Backup automatico do Aiven: habilitado no painel do servico.
- Frequencia: diaria, usando o backup automatico do provedor.
- Retencao minima: 7 dias para MVP/testes; 30 dias ou mais para producao institucional.
- Teste de restauracao: mensal ou antes de apresentacoes/deploys importantes.
- Responsavel: administrador tecnico do backend.

## Prova operacional no backend

O backend possui uma verificacao operacional para transformar a politica em
evidencia auditavel:

- variaveis de politica no deploy:
  - `BACKUP_PROVIDER`
  - `BACKUP_FREQUENCY_HOURS`
  - `BACKUP_MIN_RETENTION_DAYS`
  - `BACKUP_RETENTION_DAYS`
  - `BACKUP_RESTORE_TEST_INTERVAL_DAYS`
  - `BACKUP_LAST_RESTORE_TEST_AT`
  - `BACKUP_EVIDENCE_URL`
- componente `backup_policy` em `GET /health/detailed/`, disponivel para admin;
- task diaria `api.tasks.record_backup_operational_evidence`, agendada no
  Celery beat;
- registros de auditoria com action `backup_operational_evidence`;
- comando manual `python manage.py verify_backup_operability`.

Para considerar a prova como saudavel:

1. `BACKUP_PROVIDER` deve indicar o provedor usado, por exemplo `aiven`.
2. `BACKUP_FREQUENCY_HOURS` deve ser `24` ou menor.
3. `BACKUP_RETENTION_DAYS` deve atender `BACKUP_MIN_RETENTION_DAYS`.
4. `BACKUP_LAST_RESTORE_TEST_AT` deve conter a data ISO do ultimo teste de restore.
5. Deve existir evidencia recente em `AuditLog`, criada automaticamente pelo
   Celery beat ou manualmente pelo comando abaixo.

Registrar evidencia manual depois de conferir o painel da Aiven ou concluir um
teste de restore:

```bash
python manage.py verify_backup_operability --record --json
```

Consultar a ultima evidencia:

```bash
python manage.py shell -c "from api.models import AuditLog; print(AuditLog.objects.filter(action='backup_operational_evidence').latest('created_at').metadata)"
```

O campo `BACKUP_EVIDENCE_URL` pode apontar para um documento interno, ticket,
ata ou print armazenado fora do repositorio com a confirmacao do painel Aiven ou
do teste de restore. Nao commitar arquivos com dados pessoais ou segredos.

## Checklist no Aiven

No painel da Aiven:

1. Abra o servico MySQL usado pelo backend.
2. Confirme que backups automaticos estao ativos.
3. Registre a janela de backup e a retencao configurada.
4. Confirme que SSL esta ativo.
5. Confirme que o usuario `avnadmin` ou usuario de aplicacao tem acesso somente ao banco necessario.
6. Antes de restaurar em producao, tire um backup/export manual atual.

## Export manual do banco

Use export manual antes de operacoes arriscadas, como migracoes grandes, alteracao de schema ou restauracao.

Com variaveis carregadas no ambiente:

```bash
mysqldump \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --user="$DB_USER" \
  --password="$DB_PASSWORD" \
  --ssl-mode=REQUIRED \
  --single-transaction \
  --routines \
  --triggers \
  "$DB_NAME" > backup-miranda-YYYY-MM-DD.sql
```

No Windows PowerShell, use:

```powershell
mysqldump `
  --host="$env:DB_HOST" `
  --port="$env:DB_PORT" `
  --user="$env:DB_USER" `
  --password="$env:DB_PASSWORD" `
  --ssl-mode=REQUIRED `
  --single-transaction `
  --routines `
  --triggers `
  "$env:DB_NAME" > backup-miranda-YYYY-MM-DD.sql
```

Importante: o arquivo `.sql` pode conter dados pessoais. Nao commitar, nao enviar em chat e armazenar em local protegido.

## Restore em ambiente de teste

Antes de restaurar em producao, valide o backup em um banco temporario.

```bash
mysql \
  --host="$DB_HOST_TEST" \
  --port="$DB_PORT_TEST" \
  --user="$DB_USER_TEST" \
  --password="$DB_PASSWORD_TEST" \
  --ssl-mode=REQUIRED \
  "$DB_NAME_TEST" < backup-miranda-YYYY-MM-DD.sql
```

Depois rode:

```bash
python manage.py migrate
python manage.py check
python manage.py test api
```

Checklist de validacao:

- Login de admin funciona.
- `/api/reports/dashboard/` responde para admin.
- Comunicados publicados aparecem na API.
- Anexos abrem pelas URLs do Cloudinary.
- Logs de entrega e auditoria continuam acessiveis.

## Restore em producao

Use somente em caso de incidente confirmado ou rollback planejado.

1. Avise a equipe e pause publicacoes/envios.
2. Tire um export manual do estado atual.
3. Confirme qual backup sera restaurado.
4. Restaure pelo painel da Aiven ou usando `mysql < backup.sql`.
5. Rode migrations pendentes:

```bash
python manage.py migrate
```

6. Rode checagens:

```bash
python manage.py check
```

7. Teste login admin, listagem de comunicados e relatorios.
8. Registre a ocorrencia em auditoria operacional ou documento de incidente.

## Cloudinary

O banco guarda referencias/URLs dos arquivos, mas os arquivos ficam no Cloudinary.

Checklist:

1. Confirmar que `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` e `CLOUDINARY_API_SECRET` estao no Render.
2. Confirmar pasta configurada em `CLOUDINARY_MEDIA_FOLDER`.
3. Evitar apagar recursos diretamente no painel sem antes conferir se ainda existem registros no banco.
4. Para incidentes de arquivo apagado, restaurar pelo recurso de backup/restore do plano Cloudinary, quando disponivel.

Rotina recomendada:

- Nao usar o painel Cloudinary para limpeza manual sem checklist.
- Validar links de anexos depois de restaurar banco.
- Manter plano Cloudinary com historico/backup suficiente para o uso institucional.

## Variaveis de ambiente

Manter uma lista segura das variaveis configuradas no Render:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DB_CA_CERT
DB_SSL_REQUIRED
BACKUP_PROVIDER
BACKUP_FREQUENCY_HOURS
BACKUP_MIN_RETENTION_DAYS
BACKUP_RETENTION_DAYS
BACKUP_RESTORE_TEST_INTERVAL_DAYS
BACKUP_LAST_RESTORE_TEST_AT
BACKUP_EVIDENCE_URL
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
CLOUDINARY_MEDIA_FOLDER
FIREBASE_ENABLED
FIREBASE_PROJECT_ID
FIREBASE_CLIENT_EMAIL
FIREBASE_PRIVATE_KEY
PUSH_DISPATCH_ON_PUBLISH
EMAIL_HOST
EMAIL_PORT
EMAIL_HOST_USER
EMAIL_HOST_PASSWORD
DEFAULT_FROM_EMAIL
FRONTEND_URL
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
```

Nao commitar valores reais dessas variaveis.

## Frequencia de revisao

- Conferir backup automatico: semanalmente.
- Testar restore em ambiente de teste: mensalmente.
- Revisar lista de variaveis do Render: a cada deploy importante.
- Revisar acesso ao Aiven e Cloudinary: a cada mudanca de equipe.
