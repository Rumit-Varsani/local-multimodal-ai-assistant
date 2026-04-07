$ErrorActionPreference = "Stop"

$ProjectPath = if ($env:PROJECT_PATH) { $env:PROJECT_PATH } else { "E:\ai-server" }
$VenvPath = if ($env:VENV_PATH) { $env:VENV_PATH } else { Join-Path $ProjectPath "venv" }
$StreamlitHost = if ($env:STREAMLIT_HOST) { $env:STREAMLIT_HOST } else { "0.0.0.0" }
$StreamlitPort = if ($env:STREAMLIT_PORT) { $env:STREAMLIT_PORT } else { "8501" }
$StreamlitPath = Join-Path $VenvPath "Scripts\streamlit.exe"

if (-not (Test-Path $StreamlitPath)) {
    throw "Could not find streamlit at $StreamlitPath"
}

Set-Location $ProjectPath
Write-Host "Starting Dell-hosted Streamlit on $StreamlitHost`:$StreamlitPort"
Write-Host "Streamlit will talk to $($env:ASSISTANT_API_URL)"
& $StreamlitPath run ui/chat.py --server.address $StreamlitHost --server.port $StreamlitPort
