# Backend do Projeto Miranda

O backend possui duas implementações em Python. A aplicação Django REST
Framework é a base principal do projeto. O arquivo `fastapi_app.py` mantém um
protótipo alternativo usado para validar autenticação e operações de documentos.

## Configuração

Crie e ative um ambiente virtual dentro desta pasta:

```bash
python -m venv .venv
```

Instale as dependências do Django:

```bash
pip install -r requirements.txt
```

Copie o arquivo de exemplo e defina uma chave exclusiva para o ambiente:

```bash
cp .env.example .env
```

No Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

O `.env` não deve ser enviado ao Git. Os valores de exemplo não devem ser
reutilizados em produção.

## Django REST Framework

Com as variáveis `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` e `DB_PORT`
preenchidas, o Django utiliza MySQL. Se elas estiverem vazias, utiliza um banco
SQLite local.

Prepare o banco e inicie a aplicação:

```bash
python manage.py migrate
python manage.py runserver
```

Rotas disponíveis:

- `GET /api/hello/`: diagnóstico da API;
- `/api/documents/`: operações de documentos;
- `/api/schema/`: schema OpenAPI;
- `/api/docs/`: Swagger UI;
- `/admin/`: administração do Django.

## FastAPI

Instale as dependências adicionais:

```bash
pip install -r requirements-fastapi.txt
```

Inicie o servidor:

```bash
uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000
```

O banco padrão é criado localmente e pode ser substituído por
`FASTAPI_DATABASE_URL`. Para criar um usuário inicial, configure no `.env`:

```env
FASTAPI_ADMIN_USERNAME=administrador
FASTAPI_ADMIN_EMAIL=admin@exemplo.com
FASTAPI_ADMIN_PASSWORD=defina-uma-senha-forte
```

Sem usuário e senha configurados, a aplicação inicia sem criar credenciais
padrão.

Rotas disponíveis:

- `POST /api/register`: cadastro;
- `POST /api/login`: login;
- `GET /api/documents`: listagem de documentos;
- `POST /api/documents`: criação de documento;
- `GET`, `PUT` e `DELETE /api/documents/{id}`: manutenção de documento;
- `/docs`: Swagger UI.

## Verificações

```bash
python manage.py check
python manage.py test
python -m compileall -q .
```
