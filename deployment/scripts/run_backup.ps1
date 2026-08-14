# Runs the TruthLens daily MongoDB backup from the backend container and
# appends output to deployment\backups\backup.log. Intended to be invoked by
# the Windows Task Scheduler job created with schedule_backup.ps1, but can also
# be run manually.
param(
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

$logDir = Join-Path $RepoRoot "deployment\backups"
$log = Join-Path $logDir "backup.log"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Write-Log($msg) {
    "[$(Get-Date -Format o)] $msg" | Out-File -FilePath $log -Append -Encoding utf8
}

Write-Log "backup start"
try {
    Push-Location $RepoRoot
    & docker compose exec -T backend python deployment/scripts/backup_db.py --out /backups 2>&1 | Out-File -FilePath $log -Append -Encoding utf8
    Pop-Location
    if ($LASTEXITCODE -ne 0) {
        Write-Log "backup FAILED (exit $LASTEXITCODE)"
        exit 1
    }
    Write-Log "backup OK"
} catch {
    Write-Log "backup FAILED: $_"
    exit 1
}
