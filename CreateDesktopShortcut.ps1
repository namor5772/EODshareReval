param(
  [string]$RepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot ".")).Path,
  [string]$ShortcutName = "Run EOD + Open Report.lnk"
)

$bat = Join-Path $RepoPath "RunEODAndOpenReport.bat"
if (-not (Test-Path $bat)) { Write-Error "Batch file not found: $bat"; exit 1 }

$desktop = [Environment]::GetFolderPath('Desktop')
$lnkPath = Join-Path $desktop $ShortcutName

$wsh = New-Object -ComObject WScript.Shell
$sc = $wsh.CreateShortcut($lnkPath)
$sc.TargetPath = $bat
$sc.WorkingDirectory = $RepoPath
$sc.WindowStyle = 1
$sc.Description = "Run EOD app and open latest report in Notepad++"

$icon = "C:\Program Files\Notepad++\notepad++.exe"
if (-not (Test-Path $icon)) { $icon = "C:\Program Files (x86)\Notepad++\notepad++.exe" }
if (-not (Test-Path $icon)) { $icon = "$env:SystemRoot\System32\cmd.exe" }
$sc.IconLocation = "$icon,0"
$sc.Save()

Write-Host "Shortcut created at: $lnkPath"

