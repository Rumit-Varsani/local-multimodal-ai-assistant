# Windows Dell Runtime

## When to use this

Use this on the Dell machine if it runs Windows or PowerShell.

## Sync latest code

Preferred PowerShell command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dell_sync_main.ps1
```

## Start backend

Preferred PowerShell command:

```powershell
$env:PROJECT_PATH="E:\ai-server"
$env:ASSISTANT_HOST="0.0.0.0"
$env:ASSISTANT_PORT="8000"
powershell -ExecutionPolicy Bypass -File .\scripts\run_server_dell.ps1
```

## Start Streamlit on Dell

Use this so the UI also runs on the Dell machine and can be opened from your Mac browser:

```powershell
$env:PROJECT_PATH="E:\ai-server"
$env:ASSISTANT_API_URL="http://127.0.0.1:8000/assistant"
$env:STREAMLIT_HOST="0.0.0.0"
$env:STREAMLIT_PORT="8501"
powershell -ExecutionPolicy Bypass -File .\scripts\run_ui_dell.ps1
```

Then open this from your Mac browser:

```text
http://<DELL_IP>:8501
```

## Optional autonomy worker

Before starting the server:

```powershell
$env:AUTONOMY_AUTO_START="true"
$env:AUTONOMY_POLL_SECONDS="30"
```

Then start the backend with `run_server_dell.ps1`.

## If port 8000 is already in use

Check the process:

```powershell
netstat -ano | findstr :8000
Get-Process -Id <PID>
```

Stop the old backend if it is a stale process, then start the current server again.

## If port 8501 is already in use

Check the process:

```powershell
netstat -ano | findstr :8501
Get-Process -Id <PID>
```

Stop the stale Streamlit process, then start `run_ui_dell.ps1` again.
