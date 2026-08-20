@echo off
setlocal

cd /d "%~dp0backend"

echo Preparando o backend...
echo Instalando as dependencias do projeto...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Nao foi possivel instalar as dependencias.
  echo Verifique a mensagem de erro acima e tente novamente.
  pause
  exit /b 1
)

if not exist ".env" (
  echo.
  echo ATENCAO: o arquivo backend\.env nao foi encontrado.
  echo Crie esse arquivo e adicione as variaveis do banco, Firebase e Cloudinary.
)

echo.
echo Backend preparado.
echo Iniciando o servidor Django...
echo Quando quiser parar o servidor, pressione Ctrl+C.
REM Comando manual para iniciar o backend: python manage.py runserver
echo.
python manage.py runserver

endlocal
