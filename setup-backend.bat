@echo off
setlocal

cd /d "%~dp0backend"

echo Instalando dependencias do backend...
python -m pip install -r requirements.txt

if not exist ".env" (
  echo.
  echo ATENCAO: crie o arquivo backend\.env antes de rodar o servidor.
  echo Adicione as variaveis do banco, Firebase e Cloudinary.
)

echo.
echo Backend preparado.
echo Para iniciar:
echo cd backend
echo python manage.py runserver

endlocal
