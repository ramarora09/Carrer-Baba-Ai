$ErrorActionPreference = "Stop"

Set-Location -LiteralPath $PSScriptRoot
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:HTTP_PROXY = ""
$env:HTTPS_PROXY = ""
$env:ALL_PROXY = ""

python -m uvicorn career_baba_ai.app:app --host 127.0.0.1 --port 8011 --reload
