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
