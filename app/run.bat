@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
title AlojaGest - Hotel Cumbre Real Airport

REM ALOJAGEST - Instalacion por usuario y restauracion inicial de PostgreSQL.
REM Version 4: entorno Python local por PC, evita .venv copiado de otro equipo.
REM Windows 10/11 x64. Requiere internet solo en la primera preparacion.
REM La base queda en LOCALAPPDATA, separada de otros PostgreSQL.

set "BACKUP=%~dp0HOTEL_CUMBRE_REAL_AIRPORT.sql"
set "BASE=%LOCALAPPDATA%\AlojaGest"
set "PYTHON_DIR=%LOCALAPPDATA%\Programs\AlojaGestPython"
REM Entorno exclusivo en el perfil del PC, no dentro de la carpeta que se copia.
set "VENV_DIR=%BASE%\python-venv"
set "APP_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "ALJ_INSTALLER=%TEMP%\AlojaGestPython_%RANDOM%_%RANDOM%.exe"
set "PG_HOME=%BASE%\postgresql-18"
set "PG_BIN=%PG_HOME%\pgsql\bin"
set "PG_DATA=%BASE%\postgres-data"
set "PW_FILE=%BASE%\db-password.txt"
set "PG_ZIP=%BASE%\postgresql-18.7-win64.zip"
set "PG_DOWNLOAD=https://get.enterprisedb.com/postgresql/postgresql-18.7-1-windows-x64-binaries.zip"

REM Es un servidor PostgreSQL EXCLUSIVO para AlojaGest; no toca 5432.
set "DB_HOST=127.0.0.1"
set "DB_PORT=55432"
set "DB_USER=alojagest"
set "DB_NAME=HOTEL_CUMBRE_REAL_AIRPORT"
set "SERVER_HOST=127.0.0.1"
set "SERVER_PORT=8000"

 echo ====================================================
 echo   ALOJAGEST - Sistema Integral de Gestion Hotelera
 echo   INICIADOR V4 - PC NUEVA - ENTORNO PYTHON REPARABLE
 echo ====================================================
 echo.

if not exist "backend\server.py" (
  echo ERROR: Este archivo debe estar junto a la carpeta backend.
  goto :error_fin
)
if not exist "backend\db.py" (
  echo ERROR: Falta backend\db.py
  goto :error_fin
)
if not exist "%BACKUP%" (
  echo ERROR: Falta HOTEL_CUMBRE_REAL_AIRPORT.sql en la carpeta del BAT.
  goto :error_fin
)
if not exist "%BASE%" mkdir "%BASE%"
if errorlevel 1 goto :error_directorio

 echo [1/7] Buscando Python 3.10 o superior...
set "PYTHON_EXE="
set "PYTHON_ARG="
if exist "%PYTHON_DIR%\python.exe" (
  "%PYTHON_DIR%\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
    goto :python_ok
  )
)
py -3.12 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_EXE=py"
  set "PYTHON_ARG=-3.12"
  goto :python_ok
)
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_EXE=py"
  set "PYTHON_ARG=-3"
  goto :python_ok
)
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 (
  set "PYTHON_EXE=python"
  goto :python_ok
)
echo Instalando Python 3.12.10 para este usuario...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe' -OutFile $env:ALJ_INSTALLER"
if errorlevel 1 goto :error_python
start /wait "" "%ALJ_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=0 Include_launcher=0 Include_pip=1 Include_test=0 TargetDir="%PYTHON_DIR%"
if errorlevel 1 goto :error_python
if not exist "%PYTHON_DIR%\python.exe" goto :error_python
if exist "%ALJ_INSTALLER%" del /q "%ALJ_INSTALLER%" >nul 2>&1
set "PYTHON_EXE=%PYTHON_DIR%\python.exe"
:python_ok
echo Python disponible.

 echo.
 echo [2/7] Preparando librerias de AlojaGest...
REM Un .venv copiado de otro PC puede contener rutas C:\Users\OTRO_USUARIO.
REM Se ignora el .venv de la carpeta del proyecto. El nuestro vive en LOCALAPPDATA.
if exist "%APP_PYTHON%" (
  "%APP_PYTHON%" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
  if errorlevel 1 (
    echo El entorno Python local esta roto o pertenece a otra instalacion.
    echo Reconstruyendo SOLO las librerias locales de AlojaGest...
    rmdir /s /q "%VENV_DIR%"
    if exist "%VENV_DIR%" goto :error_librerias
  )
)
if not exist "%APP_PYTHON%" (
  echo Creando un entorno Python nuevo en: %VENV_DIR%
  "%PYTHON_EXE%" %PYTHON_ARG% -m venv "%VENV_DIR%"
  if errorlevel 1 goto :error_python
)
REM Probar que el Python del entorno realmente se ejecuta, no solo que existe.
"%APP_PYTHON%" -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 goto :error_python
"%APP_PYTHON%" -m pip --version >nul 2>&1
if errorlevel 1 (
  "%APP_PYTHON%" -m ensurepip --upgrade
  if errorlevel 1 goto :error_librerias
)
if exist "requirements.txt" (
  "%APP_PYTHON%" -m pip install --disable-pip-version-check -r "requirements.txt"
  if errorlevel 1 goto :error_librerias
)
if exist "backend\requirements.txt" (
  "%APP_PYTHON%" -m pip install --disable-pip-version-check -r "backend\requirements.txt"
  if errorlevel 1 goto :error_librerias
)
"%APP_PYTHON%" -c "import psycopg2" >nul 2>&1
if errorlevel 1 (
  "%APP_PYTHON%" -m pip install --disable-pip-version-check psycopg2-binary
  if errorlevel 1 goto :error_librerias
)
"%APP_PYTHON%" -c "import pathlib,sys; sys.exit(0 if pathlib.Path('HOTEL_CUMBRE_REAL_AIRPORT.sql').read_bytes()[:5] == b'PGDMP' else 1)" >nul 2>&1
if errorlevel 1 (
  echo ERROR: El archivo adjunto NO es el backup PGDMP esperado.
  echo No se intentara restaurar, para proteger sus datos.
  goto :error_fin
)

 echo.
 echo [3/7] Preparando PostgreSQL 18 exclusivo para AlojaGest...
REM Se pueden aprovechar binarios PostgreSQL 18 ya presentes en el PC.
if not exist "%PG_BIN%\pg_restore.exe" (
  if exist "%ProgramFiles%\PostgreSQL\18\bin\pg_restore.exe" (
    set "PG_BIN=%ProgramFiles%\PostgreSQL\18\bin"
  )
)
if not exist "%PG_BIN%\pg_restore.exe" (
  echo Descargando PostgreSQL 18.7 desde EnterpriseDB.
  echo Es una descarga grande, necesaria solo la primera vez.
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -UseBasicParsing -Uri $env:PG_DOWNLOAD -OutFile $env:PG_ZIP; Invoke-WebRequest -UseBasicParsing -Uri ($env:PG_DOWNLOAD + '.sha256') -OutFile ($env:PG_ZIP + '.sha256'); $expected=[regex]::Match((Get-Content ($env:PG_ZIP + '.sha256') -Raw),'(?i)[a-f0-9]{64}').Value; $actual=(Get-FileHash -Path $env:PG_ZIP -Algorithm SHA256).Hash; if(-not $expected -or $expected -ne $actual){throw 'Verificacion SHA256 incorrecta'}; Write-Host 'Descarga verificada.'"
  if errorlevel 1 goto :error_descarga_pg
  echo Extrayendo PostgreSQL en el perfil del usuario...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; Expand-Archive -LiteralPath $env:PG_ZIP -DestinationPath $env:PG_HOME -Force"
  if errorlevel 1 goto :error_descarga_pg
)
if not exist "%PG_BIN%\initdb.exe" goto :error_pg_bin
if not exist "%PG_BIN%\pg_ctl.exe" goto :error_pg_bin
if not exist "%PG_BIN%\pg_restore.exe" goto :error_pg_bin
if not exist "%PG_BIN%\psql.exe" goto :error_pg_bin
if not exist "%PG_BIN%\createdb.exe" goto :error_pg_bin
set "PATH=%PG_BIN%;%PATH%"
"%PG_BIN%\pg_restore.exe" --version
if errorlevel 1 goto :error_pg_bin

 echo.
 echo [4/7] Iniciando base de datos local en puerto 55432...
REM Conservar la contrasena entre sesiones; nunca regenerar si hay datos.
if exist "%PG_DATA%\PG_VERSION" (
  if not exist "%PW_FILE%" (
    echo ERROR: Ya hay datos pero se perdio db-password.txt.
    echo No se borrara ni reinicializara la base.
    goto :error_fin
  )
) else (
  if exist "%PG_DATA%" (
    echo ERROR: Carpeta de datos incompleta: %PG_DATA%
    echo No se borrara ni reemplazara automaticamente.
    goto :error_fin
  )
  echo Inicializando PostgreSQL sin pedir permisos de administrador...
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; ([guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')) | Set-Content -LiteralPath $env:PW_FILE -Encoding ASCII -NoNewline"
  if errorlevel 1 goto :error_pg_data
  "%PG_BIN%\initdb.exe" -D "%PG_DATA%" -U alojagest --encoding=UTF8 --locale=C --auth-host=scram-sha-256 --auth-local=scram-sha-256 --pwfile="%PW_FILE%" --no-instructions
  if errorlevel 1 goto :error_pg_data
)
set "DB_PASSWORD="
for /f "usebackq delims=" %%P in ("%PW_FILE%") do set "DB_PASSWORD=%%P"
if not defined DB_PASSWORD goto :error_pg_data
set "PGPASSWORD=%DB_PASSWORD%"
"%PG_BIN%\pg_ctl.exe" -D "%PG_DATA%" status >nul 2>&1
if errorlevel 1 (
  "%PG_BIN%\pg_ctl.exe" -D "%PG_DATA%" -l "%BASE%\postgres.log" -o "-h 127.0.0.1 -p 55432" -w -t 60 start
  if errorlevel 1 goto :error_pg_start
)
"%PG_BIN%\psql.exe" -X -w -q -h 127.0.0.1 -p 55432 -U alojagest -d postgres -v ON_ERROR_STOP=1 -c "SELECT 1;" >nul
if errorlevel 1 goto :error_pg_start

 echo.
 echo [5/7] Restaurando backup solo si la base esta vacia...
REM Emplear psql en lugar de Python -c para evitar errores de comillas.
REM Si la base existe, no la borra ni modifica sus datos.
set "DB_STATUS_FILE=%BASE%\db-exists.tmp"
"%PG_BIN%\psql.exe" -X -w -q -t -A -v ON_ERROR_STOP=1 -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d postgres -c "SELECT COUNT(*) FROM pg_database WHERE datname='%DB_NAME%';" > "%DB_STATUS_FILE%"
if errorlevel 1 goto :error_bd
set "DB_EXISTS="
set /p "DB_EXISTS=" < "%DB_STATUS_FILE%"
if "%DB_EXISTS%"=="0" (
  echo Creando base de datos %DB_NAME%...
  "%PG_BIN%\createdb.exe" -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" --maintenance-db=postgres "%DB_NAME%"
  if errorlevel 1 goto :error_bd
) else if "%DB_EXISTS%"=="1" (
  echo Base de datos encontrada. Comprobando sus tablas...
) else (
  echo ERROR: No se pudo interpretar el estado de la base de datos.
  goto :error_bd
)

set "TABLE_STATUS_FILE=%BASE%\table-count.tmp"
"%PG_BIN%\psql.exe" -X -w -q -t -A -v ON_ERROR_STOP=1 -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -c "SELECT COUNT(*) FROM pg_catalog.pg_tables WHERE schemaname='public';" > "%TABLE_STATUS_FILE%"
if errorlevel 1 goto :error_bd
set "TABLE_COUNT="
set /p "TABLE_COUNT=" < "%TABLE_STATUS_FILE%"
echo Tablas existentes: %TABLE_COUNT%
if "%TABLE_COUNT%"=="0" goto :restaurar_bd
if not defined TABLE_COUNT goto :error_bd
goto :bd_existente

:restaurar_bd
echo Base vacia. Restaurando el backup original con pg_restore...
REM Restauracion atomica: si falla, se deshacen los cambios de la restauracion.
"%PG_BIN%\pg_restore.exe" --exit-on-error --single-transaction --no-owner --no-privileges -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" "%BACKUP%"
if errorlevel 1 goto :error_restore

REM Solo actualiza credenciales si el backup no incluye la columna usuario.
set "AUTH_STATUS_FILE=%BASE%\auth-count.tmp"
"%PG_BIN%\psql.exe" -X -w -q -t -A -v ON_ERROR_STOP=1 -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -c "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='Recepcionista' AND column_name='usuario';" > "%AUTH_STATUS_FILE%"
if errorlevel 1 goto :error_bd
set "AUTH_COUNT="
set /p "AUTH_COUNT=" < "%AUTH_STATUS_FILE%"
if "%AUTH_COUNT%"=="0" (
  echo Aplicando actualizacion de usuarios y roles...
  "%APP_PYTHON%" "database\upgrade_auth_employees.py"
  if errorlevel 1 goto :error_bd
) else if not "%AUTH_COUNT%"=="1" (
  echo ERROR: No se pudo verificar el modulo de autenticacion.
  goto :error_bd
)
echo Backup restaurado correctamente.
goto :verificar_bd

:bd_existente
echo La BD ya contiene tablas. NO se sobrescribiran sus datos.

:verificar_bd
 echo.
 echo [6/7] Verificando las tablas principales...
set "SCHEMA_STATUS_FILE=%BASE%\schema-count.tmp"
"%PG_BIN%\psql.exe" -X -w -q -t -A -v ON_ERROR_STOP=1 -h "%DB_HOST%" -p "%DB_PORT%" -U "%DB_USER%" -d "%DB_NAME%" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('Reserva','Habitacion','Recepcionista','auditoria_operaciones');" > "%SCHEMA_STATUS_FILE%"
if errorlevel 1 goto :error_bd
set "SCHEMA_COUNT="
set /p "SCHEMA_COUNT=" < "%SCHEMA_STATUS_FILE%"
if not "%SCHEMA_COUNT%"=="4" (
  echo ERROR: Se esperaban las tablas Reserva, Habitacion, Recepcionista y auditoria_operaciones.
  echo Tablas principales presentes: %SCHEMA_COUNT% de 4.
  goto :error_bd
)
echo Tablas principales verificadas correctamente.

 echo [7/7] Iniciando AlojaGest: http://localhost:8000
 echo Credenciales de prueba (si corresponden al backup):
 echo   Administrador: admin / admin
 echo   Recepcionista: E002 / 70000002
 echo.
 echo Mantenga esta ventana abierta mientras use el sistema.
 echo La BD se conservara en: %PG_DATA%
 echo.
start "" /min powershell -NoProfile -WindowStyle Hidden -Command "for($i=0;$i -lt 40;$i++){try{$t=[Net.Sockets.TcpClient]::new('127.0.0.1',8000);$t.Close();Start-Process 'http://localhost:8000';break}catch{Start-Sleep -Seconds 1}}"
"%APP_PYTHON%" "backend\server.py"
if errorlevel 1 (
  echo ERROR: El servidor AlojaGest se detuvo de forma inesperada.
  goto :error_fin
)
echo Servidor cerrado.
pause
exit /b 0

:error_directorio
echo ERROR: No pudo crearse la carpeta de instalacion local.
goto :error_fin
:error_python
echo ERROR: No fue posible preparar Python.
goto :error_fin
:error_librerias
echo ERROR: Fallo la instalacion de librerias de Python.
echo Revise la conexion a Internet y cierre otras instancias de AlojaGest.
goto :error_fin
:error_descarga_pg
echo ERROR: No se pudo descargar, verificar o extraer PostgreSQL 18.7.
echo Revise la conexion a Internet y el espacio libre.
goto :error_fin
:error_pg_bin
echo ERROR: No se encontraron los ejecutables completos de PostgreSQL 18.
goto :error_fin
:error_pg_data
echo ERROR: No se pudo inicializar PostgreSQL. Revise el mensaje anterior.
echo No borre la carpeta de datos sin una copia de seguridad.
goto :error_fin
:error_pg_start
echo ERROR: PostgreSQL no pudo iniciarse en el puerto 55432.
echo Revise %BASE%\postgres.log
goto :error_fin
:error_bd
echo ERROR: La BD no esta disponible o tiene una estructura incompleta.
echo NO se han borrado datos existentes.
goto :error_fin
:error_restore
echo ERROR: Fallo la restauracion. Se detiene para proteger los datos.
echo El backup permanece intacto y se puede reintentar.
goto :error_fin
:error_fin
if exist "%ALJ_INSTALLER%" del /q "%ALJ_INSTALLER%" >nul 2>&1
echo.
pause
exit /b 1
