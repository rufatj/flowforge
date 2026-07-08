# Native (no-Docker) equivalent of docker-compose.n8n-test.yml.
# Runs a throwaway n8n on http://localhost:5679 for gate-3 import testing.
# Same pinned N8N_ENCRYPTION_KEY and same ./n8n-test-data folder, so you can
# switch to the Docker version later without losing the owner account or API keys.
#
#   powershell -ExecutionPolicy Bypass -File run-n8n-test.ps1

$env:N8N_ENCRYPTION_KEY = "flowforge-hackathon-fixed-key-2026"
$env:N8N_USER_FOLDER = Join-Path $PSScriptRoot "n8n-test-data"
$env:N8N_PORT = "5679"
$env:N8N_HOST = "localhost"
$env:N8N_PROTOCOL = "http"
$env:N8N_SECURE_COOKIE = "false"
$env:N8N_DIAGNOSTICS_ENABLED = "false"
$env:N8N_PUBLIC_API_DISABLED = "false"
$env:WEBHOOK_URL = "http://localhost:5679/"
$env:GENERIC_TIMEZONE = "UTC"
$env:DB_SQLITE_POOL_SIZE = "5"
# n8n's internal task broker ALSO defaults to port 5679 — move it off the UI port.
$env:N8N_RUNNERS_BROKER_PORT = "5680"

n8n start
