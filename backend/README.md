# Back-End | [cite_start]Aplicativo Oficial de Comunicação Institucional [cite: 46]

Este é o motor do sistema de comunicação governamental, estruturado em **Django REST Framework** e **MySQL**. 

⚠️ **Atenção Equipe:** O uso do Google Colab e do MongoDB foi descontinuado por incompatibilidade com requisitos de auditoria e segurança relacional. Siga rigorosamente os passos abaixo para rodar a API na sua máquina.

## 1. Pré-requisitos de Sistema (Importante)
A biblioteca `mysqlclient` exige compiladores C/C++ do sistema operacional.
- **Linux (Ubuntu/Debian):** Execute no terminal antes de instalar o Python:
  `sudo apt-get update && sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config`
- **Windows:** É necessário ter o *Visual Studio Build Tools* (C++) instalado.

## 2. Configuração do Ambiente Local
Não instale pacotes globalmente. Use o ambiente virtual isolado.

```bash
# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente
source venv/bin/activate  # No Linux/Mac
venv\Scripts\activate     # No Windows

# Instale as dependências
pip install -r requirements.txt 
```

## 3.O Cofre de Senhas (.env)
Você precisa criar um arquivo chamado .env na raiz da pasta backend. Ele já está ignorado pelo Git para não vazar senhas. Peça as credenciais do banco de dados ao Inácio ou configure o seu MySQL local com os seguintes dados e preencha o arquivo:
DB_NAME=miranda_db
DB_USER=miranda_dev
DB_PASSWORD=SuaSenhaForteAqui
DB_HOST=127.0.0.1
DB_PORT=3306

## 4. Inicializando o Banco de Dados
Com o .env configurado e o MySQL rodando na sua máquina, aplique as tabelas:
python manage.py makemigrations
python manage.py migrate

## 5. Rodando o Servidor e Documentação (Swagger)
Para subir a API, execute:
python manage.py runserver

Painel Administrativo: http://127.0.0.1:8000/admin/

Documentação da API (Para o Front-End): http://127.0.0.1:8000/api/docs/ -> O Tagor deve consultar esta URL para ver os contratos JSON exatos de cada rota.

## 6. Push Notification com Firebase
O backend dispara push automaticamente quando um comunicado e publicado. Para ativar o envio real em producao, configure:

```env
PUSH_DISPATCH_ON_PUBLISH=true
PUSH_DISPATCH_ASYNC=true
REDIS_URL=redis://...
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID=seu-projeto-firebase
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@seu-projeto.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

Se `FIREBASE_ENABLED=false` ou as credenciais estiverem ausentes, o backend cria os logs de entrega e deixa as notificacoes como pendentes. O gestor ainda pode tentar o envio manual pelo endpoint:

```http
POST /api/announcements/{id}/dispatch/
```

Com `PUSH_DISPATCH_ASYNC=true`, a publicacao do comunicado apenas enfileira a entrega. Rode um worker para processar os envios:

```bash
celery -A core worker --loglevel=info
```

Para as rotinas periodicas de retry, limpeza de logs antigos e marcacao de entregas pendentes antigas, rode tambem:

```bash
celery -A core beat --loglevel=info
```

## 7. Gestao de administradores
Administradores autenticados podem gerenciar gestores autorizados pela API:

```http
GET /api/managers/
POST /api/managers/
PATCH /api/managers/{id}/
POST /api/managers/{id}/deactivate/
POST /api/managers/{id}/reactivate/
POST /api/managers/{id}/revoke/
```

Criacao minima:

```json
{
  "username": "novo_gestor",
  "email": "novo_gestor@example.com",
  "password": "SenhaForte123",
  "first_name": "Novo Gestor",
  "phone_number": "51999999999"
}
```

`deactivate` bloqueia o login do gestor. `revoke` remove o acesso administrativo, apaga tokens ativos e transforma o perfil em cidadao.

Politica de token para gestores:

```env
MANAGER_TOKEN_TTL_SECONDS=28800
MANAGER_TOKEN_ROTATE_ON_LOGIN=true
```

Gestores recebem token novo a cada login. Tokens expirados sao recusados e revogados automaticamente. Reset de senha tambem revoga tokens existentes.

## 8. LGPD e auditoria
Administradores podem consultar trilhas de auditoria pela API:

```http
GET /api/audit-logs/
```

Cidadaos autenticados podem abrir solicitacoes LGPD e consultar as proprias solicitacoes:

```http
GET /api/privacy-requests/
POST /api/privacy-requests/
POST /api/privacy/deactivate-account/
```

Tipos de solicitacao LGPD:

```text
erasure
export
deactivation
```

Administradores podem concluir ou rejeitar uma solicitacao:

```http
POST /api/privacy-requests/{id}/complete/
POST /api/privacy-requests/{id}/reject/
```

O backend registra auditoria para criacao/publicacao/envio de comunicados, alteracoes de identidade visual, gestao de administradores, solicitacoes LGPD e desativacao de conta pelo proprio cidadao.

A politica operacional LGPD esta documentada em:

```text
backend/docs/LGPD_POLICY.md
```

## 9. Segmentacao de envio
Administradores podem criar segmentos para enviar comunicados a grupos especificos:

```http
GET /api/segments/
POST /api/segments/
PATCH /api/segments/{id}/
```

Um segmento pode conter usuarios e/ou dispositivos push. Ao criar ou editar um comunicado, informe `segments` com IDs dos segmentos:

```json
{
  "title": "Comunicado do bairro",
  "content": "Mensagem oficial.",
  "status": "draft",
  "segments": [1, 2]
}
```

Se `segments` estiver vazio ou ausente, o comunicado e enviado para todos os dispositivos ativos.

## 10. Backup e restauracao
O procedimento operacional de backup e restore esta documentado em:

```text
backend/docs/BACKUP_RESTORE.md
```

Politica minima do MVP:

- backup automatico diario no Aiven;
- retencao minima de 7 dias em testes/MVP e 30 dias ou mais em producao;
- teste mensal de restore em ambiente separado;
- arquivos mantidos no Cloudinary, com cuidado para nao apagar recursos manualmente;
- variaveis do Render documentadas fora do Git, sem segredos no repositorio.

## 11. Guia final de producao
O guia consolidado de deploy e operacao em producao esta em:

```text
backend/docs/PRODUCTION_DEPLOYMENT.md
```

Ele cobre variaveis do Render, deploy, migrations, admin inicial, Cloudinary, Firebase, SMTP, URLs principais e checklist pos-deploy.

### O Fluxo Final do Git
Com os arquivos criados e salvos, execute a sequência de salvamento na sua *branch* de infraestrutura:

```bash
git add .gitignore README.md
git commit -m "chore: adiciona gitignore rigoroso e documentacao arquitetural no readme"
git push origin chore/estruturacao-arquitetura
```
