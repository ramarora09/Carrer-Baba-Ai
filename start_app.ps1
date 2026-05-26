$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONDONTWRITEBYTECODE = "1"

python -m uvicorn career_baba_ai.app:app --host 127.0.0.1 --port 8010 --reload
