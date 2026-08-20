# Projeto Miranda

Aplicação full stack em desenvolvimento para comunicação interna e organização
de documentos. O repositório reúne uma interface em React e duas experiências
de backend em Python: uma API principal com Django REST Framework e um protótipo
alternativo com FastAPI.

## Estado atual

O frontend possui telas de abertura, login, cadastro e uma área inicial após a
autenticação. A estrutura está organizada por funcionalidades, com componentes,
hooks, serviços, tipos e rotas separados.

O backend Django disponibiliza documentação Swagger, uma rota de diagnóstico e
um CRUD de documentos. O protótipo FastAPI inclui cadastro, login e operações
de documentos em um banco local. Os contratos de autenticação das duas APIs
ainda precisam ser unificados antes da integração ser considerada concluída.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Frontend | React 19, TypeScript, Vite, React Router e Axios |
| Backend principal | Python, Django e Django REST Framework |
| Backend alternativo | FastAPI, SQLAlchemy e Pydantic |
| Banco de dados | MySQL ou SQLite no desenvolvimento |
| Documentação | drf-spectacular e Swagger UI |
| Qualidade | ESLint, TypeScript e GitHub Actions |

## Estrutura

```text
.
├── backend/
│   ├── api/
│   ├── core/
│   ├── fastapi_app.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
└── .github/workflows/
```

## Configuração do backend

Entre na pasta do backend, crie o ambiente virtual e instale as dependências:

```bash
cd backend
python -m venv .venv
```

Linux ou macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Depois, instale as dependências e crie o arquivo local de configuração:

```bash
pip install -r requirements.txt
cp .env.example .env
```

No Windows, use `Copy-Item .env.example .env` para copiar o arquivo. Antes de
iniciar a API, substitua no `.env` o valor de `DJANGO_SECRET_KEY`.

### Django REST Framework

```bash
python manage.py migrate
python manage.py runserver
```

Endereços locais:

- API: `http://127.0.0.1:8000/api/`;
- documentação: `http://127.0.0.1:8000/api/docs/`;
- administração Django: `http://127.0.0.1:8000/admin/`.

Se as variáveis `DB_*` estiverem vazias, o Django usa SQLite. Para trabalhar
com MySQL, preencha todas as variáveis de conexão no `.env`.

### FastAPI

Instale as dependências adicionais e inicie o servidor:

```bash
pip install -r requirements-fastapi.txt
uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000
```

A documentação fica em `http://127.0.0.1:8000/docs`. O usuário inicial só é
criado quando `FASTAPI_ADMIN_USERNAME` e `FASTAPI_ADMIN_PASSWORD` são definidos
no `.env`.

## Configuração do frontend

```bash
cd frontend
npm ci
```

Copie `.env.example` para `.env` e inicie o Vite:

```bash
npm run dev
```

O frontend abre em `http://localhost:5173`. A URL da API pode ser alterada pela
variável `VITE_API_BASE_URL`.

## Verificações de qualidade

Frontend:

```bash
cd frontend
npm run lint
npm run build
```

Backend:

```bash
cd backend
python manage.py check
python manage.py test
python -m compileall -q .
```

O GitHub Actions executa essas verificações em Pull Requests e em alterações
enviadas para a branch `main`.

## Segurança

- chaves e senhas são lidas de variáveis de ambiente;
- os arquivos `.env` não são versionados;
- bancos SQLite de desenvolvimento não fazem parte do repositório;
- o FastAPI não cria usuário com senha padrão;
- exemplos de configuração não contêm credenciais reais.

Mais detalhes estão na [documentação do backend](backend/README.md).
