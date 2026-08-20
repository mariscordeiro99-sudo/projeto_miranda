# Backend do Projeto Miranda

API do sistema interno de comunicação institucional, desenvolvida com Django e Django REST Framework.

## Recursos principais

- autenticação e controle de acesso por perfil;
- comunicados, anexos e segmentação de destinatários;
- mensagens internas;
- gestão de identidade visual;
- notificações e registros de entrega;
- trilha de auditoria e solicitações relacionadas à LGPD;
- rotinas de backup, restauração e verificação de saúde;
- validação e compressão de mídia.

## Requisitos

- Python 3.12 ou superior;
- FFmpeg para processamento de vídeo;
- SQLite para desenvolvimento ou MySQL para ambientes integrados;
- Redis quando filas assíncronas estiverem habilitadas.

## Ambiente local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

No Windows, ative o ambiente com `.venv\\Scripts\\activate`.

O arquivo `.env.example` contém apenas nomes e valores de exemplo. Credenciais reais devem permanecer no gerenciador seguro de cada ambiente e nunca devem ser adicionadas ao Git.

## Endereços locais

- API: `http://127.0.0.1:8000/api/`
- painel administrativo: `http://127.0.0.1:8000/admin/`
- documentação OpenAPI: `http://127.0.0.1:8000/api/docs/`
- verificação de saúde: `http://127.0.0.1:8000/health/`

## Qualidade

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m compileall -q .
```

## Operação

Os procedimentos detalhados ficam em `docs/`:

- `BACKUP_RESTORE.md` — backup e restauração;
- `LGPD_POLICY.md` — controles e operação relacionados à LGPD;
- `PRODUCTION_DEPLOYMENT.md` — configuração de produção;
- `AIVEN_SSL_TROUBLESHOOTING.md` — conexão segura com MySQL.

Este sistema foi projetado para uso institucional controlado. A disponibilidade externa de uma implantação não substitui autenticação, autorização nem a configuração adequada das permissões.
