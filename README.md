# Projeto Miranda

Plataforma interna de comunicação e gestão institucional. O sistema centraliza comunicados, mensagens, anexos e controles administrativos em uma aplicação full stack.

## Funcionalidades

- autenticação e perfis com diferentes níveis de acesso;
- publicação e segmentação de comunicados;
- mensagens internas e envio de anexos;
- gestão de usuários e identidade visual;
- registros de entrega, auditoria e solicitações relacionadas à LGPD;
- notificações, processamento de vídeos e rotinas de backup;
- documentação da API e verificações de saúde da aplicação.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Frontend | React, TypeScript, Vite e Axios |
| Backend | Python, Django e Django REST Framework |
| Dados e filas | MySQL, Redis e Celery |
| Infraestrutura | Docker, Cloudinary e Render |
| Qualidade | ESLint, testes Django e GitHub Actions |

## Estrutura

```text
backend/    API, regras de negócio, migrações, testes e documentação
frontend/   interface React e integração com a API
```

## Execução local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm ci
cp .env.example .env
npm run dev
```

No Windows, ative o ambiente Python com `.venv\\Scripts\\activate`.

## Validação

```bash
# backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test

# frontend
npm run lint
npm run build
```

## Segurança

Arquivos `.env`, bancos locais, chaves e certificados não devem ser versionados. Os arquivos `.env.example` documentam somente os nomes das variáveis e usam valores fictícios.

O Projeto Miranda é destinado a ambientes institucionais com acesso controlado. Cada implantação deve configurar corretamente autenticação, autorização, origens permitidas, SSL e gestão de credenciais.
