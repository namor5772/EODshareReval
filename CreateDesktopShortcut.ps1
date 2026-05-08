param(
  [string]$RepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot ".")).Path,
  [string]$ShortcutName = "Run EOD + Open Report.lnk"
)

$bat = Join-Path $RepoPath "run_eod_downloader_and_report.bat"
if (-not (Test-Path $bat)) { Write-Error "Batch file not found: $bat"; exit 1 }

# Silent launcher: wscript.exe runs the .vbs which spawns the .bat hidden,
# so no console flashes when the user double-clicks the shortcut.
$vbs = Join-Path $RepoPath "run_eod_hidden.vbs"
if (-not (Test-Path $vbs)) { Write-Error "VBS launcher not found: $vbs"; exit 1 }
$wscriptExe = Join-Path $env:SystemRoot 'System32\wscript.exe'

$desktop = [Environment]::GetFolderPath('Desktop')
$lnkPath = Join-Path $desktop $ShortcutName

$wsh = New-Object -ComObject WScript.Shell
$sc = $wsh.CreateShortcut($lnkPath)
$sc.TargetPath = $wscriptExe
$sc.Arguments = '"' + $vbs + '"'
$sc.WorkingDirectory = $RepoPath
$sc.WindowStyle = 1
$sc.Description = "Run EOD app silently and open latest report in Notepad++"

# Prefer the custom ASX-themed icon shipped with the repo; fall back to Notepad++,
# then to a generic system icon if neither exists.
$customIco = Join-Path $RepoPath "eod_icon.ico"
if (Test-Path $customIco) {
    $sc.IconLocation = "$customIco,0"
} else {
    $icon = "C:\Program Files\Notepad++\notepad++.exe"
    if (-not (Test-Path $icon)) { $icon = "C:\Program Files (x86)\Notepad++\notepad++.exe" }
    if (-not (Test-Path $icon)) { $icon = "$env:SystemRoot\System32\cmd.exe" }
    $sc.IconLocation = "$icon,0"
}
$sc.Save()

Write-Host "Shortcut created at: $lnkPath"

