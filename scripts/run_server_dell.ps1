$ErrorActionPreference = "Stop"

$ProjectPath = if ($env:PROJECT_PATH) { $env:PROJECT_PATH } else { "E:\ai-server" }
$VenvPath = if ($env:VENV_PATH) { $env:VENV_PATH } else { Join-Path $ProjectPath "venv" }
$HostValue = if ($env:ASSISTANT_HOST) { $env:ASSISTANT_HOST } else { "0.0.0.0" }
$PortValue = if ($env:ASSISTANT_PORT) { $env:ASSISTANT_PORT } else { "8000" }

$UvicornPath = Join-Path $VenvPath "Scripts\uvicorn.exe"

if (-not (Test-Path $UvicornPath)) {
    throw "Could not find uvicorn at $UvicornPath"
}

Set-Location $ProjectPath
Write-Host "Starting FastAPI on $HostValue`:$PortValue from $ProjectPath"
& $UvicornPath backend.main:app --host $HostValue --port $PortValue
