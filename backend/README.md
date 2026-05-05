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

### O Fluxo Final do Git
Com os arquivos criados e salvos, execute a sequência de salvamento na sua *branch* de infraestrutura:

```bash
git add .gitignore README.md
git commit -m "chore: adiciona gitignore rigoroso e documentacao arquitetural no readme"
git push origin chore/estruturacao-arquitetura
```