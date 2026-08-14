# Registers (or removes) a Windows Task Scheduler job that runs the TruthLens
# daily MongoDB backup via run_backup.ps1. Requires an elevated PowerShell.
#
#   .\schedule_backup.ps1                     # daily at 02:00 (default)
#   .\schedule_backup.ps1 -Time "03:30"
#   .\schedule_backup.ps1 -Unregister         # remove the scheduled job
param(
    [string]$TaskName = "TruthLensDBBackup",
    [string]$Time = "02:00",
    [string]$RepoRoot = "",
    [switch]$Unregister
)

if (-not $RepoRoot) {
    $RepoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

if ($Unregister) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Output "Removed scheduled task '$TaskName'."
    exit 0
}

$script = Join-Path $PSScriptRoot "run_backup.ps1"
if (-not (Test-Path -LiteralPath $script)) {
    Write-Error "run_backup.ps1 not found: $script"
    exit 1
}

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`"" `
    -WorkingDirectory $RepoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Principal $principal -Description "TruthLens daily MongoDB backup" -Force | Out-Null
Write-Output "Registered '$TaskName' daily at $Time (working dir: $RepoRoot)."
