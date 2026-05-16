$root = $PSScriptRoot

function Write-Step($msg) { Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    $msg" -ForegroundColor Yellow }

# ── 1. Infra ────────────────────────────────────────────────────────────────
Write-Step "Subindo PostgreSQL e RabbitMQ..."
docker compose up db rabbitmq -d

Write-Step "Aguardando PostgreSQL ficar saudável..."
$timeout = 60
$elapsed = 0
while ($elapsed -lt $timeout) {
    $status = docker inspect keltech_db --format '{{.State.Health.Status}}' 2>$null
    if ($status -eq 'healthy') { break }
    Write-Host "    aguardando... ($elapsed s)" -ForegroundColor DarkGray
    Start-Sleep 3
    $elapsed += 3
}
if ($elapsed -ge $timeout) {
    Write-Host "ERRO: PostgreSQL nao ficou saudavel." -ForegroundColor Red
    exit 1
}
Write-Ok "PostgreSQL pronto."

# ── 2. Variáveis locais (localhost em vez dos hostnames Docker) ───────────────
$localEnv = @"
`$env:DATABASE_URL  = 'postgresql+asyncpg://keltech:keltech@localhost:5432/keltech'
`$env:RABBITMQ_URL  = 'amqp://keltech:keltech@localhost:5672/'
`$env:DB_HOST       = 'localhost'
`$env:RABBITMQ_HOST = 'localhost'
`$env:SECRET_KEY    = 'dev-secret-key-not-for-production'
`$env:APP_ENV       = 'development'
`$env:UPLOADS_DIR   = 'uploads'
`$env:PYTHONPATH    = '$root'
"@

# ── 3. Instalar deps do worker (só na primeira vez) ──────────────────────────
Write-Step "Verificando dependências do worker..."
$hasPaddle = uv pip show paddleocr 2>$null
if (-not $hasPaddle) {
    Write-Warn "Instalando paddleocr, pymupdf e opencv (pode demorar alguns minutos)..."
    uv pip install -r requirements-worker.txt
} else {
    Write-Ok "Dependências do worker já instaladas."
}

# ── 4. Abre janelas separadas ────────────────────────────────────────────────
Write-Step "Abrindo janelas..."

# API — exclui .venv do watcher para não recarregar com arquivos do paddleocr
$api = @"
Set-Location '$root'
$localEnv
Write-Host '=== API FastAPI ===' -ForegroundColor Cyan
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude '.venv' --reload-exclude 'uploads'
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $api

# OCR Worker
$worker = @"
Set-Location '$root'
$localEnv
Write-Host '=== OCR Worker ===' -ForegroundColor Magenta
uv run python -m src.worker.main
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $worker

# Frontend Vite
$frontend = @"
Set-Location '$root\src\frontend'
Write-Host '=== Vite Frontend ===' -ForegroundColor Yellow
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontend

# ── 5. Resumo ────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor DarkGray
Write-Host "  Todos os servicos iniciados" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor DarkGray
Write-Host "  API      ->  http://localhost:8000"
Write-Host "  Swagger  ->  http://localhost:8000/docs"
Write-Host "  Frontend ->  http://localhost:5173"
Write-Host "  RabbitMQ ->  http://localhost:15672  (keltech/keltech)"
Write-Host "========================================" -ForegroundColor DarkGray
Write-Host ""
Write-Warn "Para parar a infra: docker compose down"
