# VEIL Windows computer inventory — read-only, no administrator rights required
# Writes only RAM, logical CPU cores and free space on the Windows system drive.
# Does NOT collect serial numbers, device identifiers, user names or file contents.
# Usage (PowerShell): powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\windows_hardware_inventory.ps1
# Review the printed JSON before sharing it with anyone.
$ErrorActionPreference = 'Stop'
try {
    $os = Get-CimInstance Win32_OperatingSystem
    $cpus = @(Get-CimInstance Win32_Processor)
    $driveLetter = $env:SystemDrive
    if (-not $driveLetter) { throw 'SystemDrive is not set' }
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$driveLetter'"
    if ($null -eq $disk -or $null -eq $disk.FreeSpace) {
        throw 'Could not determine system-drive free space'
    }
    $ram = [math]::Round([double]$os.TotalVisibleMemorySize / 1MB, 2) # KB -> GiB
    $logical = ($cpus | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
    $free = [math]::Round([double]$disk.FreeSpace / 1GB, 2)
    $spec = [ordered]@{
        ram_gb = $ram
        free_storage_gb = $free
        logical_cores = [int]$logical
    }
    $json = $spec | ConvertTo-Json
    Write-Output $json
    Write-Host 'Copy this JSON into a local file and run tools/hardware_triage.py on it.' -ForegroundColor Cyan
} catch {
    Write-Error "Inventory failed: $($_.Exception.Message)"
    exit 1
}
