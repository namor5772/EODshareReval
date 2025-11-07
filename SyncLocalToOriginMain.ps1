param(
  [string]$RepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot ".")).Path,
  [string]$Remote = "origin",
  [string]$Branch = "main",
  [switch]$Clean,
  [switch]$CleanIgnored,
  [switch]$NoStash
)

Write-Host "[Sync] Repo:   $RepoPath"
Write-Host "[Sync] Remote: $Remote    Branch: $Branch"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "git not found in PATH. Install Git and retry."; exit 1
}

Set-Location -LiteralPath $RepoPath

$inside = git rev-parse --is-inside-work-tree 2>$null
if (-not $inside -or $inside.Trim().ToLower() -ne 'true') {
  Write-Error "Not a Git repository: $RepoPath"; exit 1
}

Write-Host "[Sync] Fetching from $Remote..."
& git fetch $Remote --prune | Out-Host
if ($LASTEXITCODE -ne 0) { Write-Error "git fetch failed."; exit $LASTEXITCODE }

& git show-ref --verify --quiet "refs/remotes/$Remote/$Branch"
if ($LASTEXITCODE -ne 0) { Write-Error "Remote branch $Remote/$Branch not found."; exit 1 }

if (-not $NoStash) {
  $changes = git status --porcelain
  if ($changes) {
    $ts = Get-Date -Format yyyyMMddHHmmss
    $msg = "pre-reset-$ts"
    Write-Host "[Sync] Stashing uncommitted changes as: $msg"
    & git stash push -u -m $msg | Out-Host
    if ($LASTEXITCODE -ne 0) { Write-Error "git stash failed."; exit $LASTEXITCODE }
  } else {
    Write-Host "[Sync] Working tree clean; no stash needed."
  }
} else {
  Write-Host "[Sync] Skipping stash (NoStash)."
}

Write-Host "[Sync] Forcing local $Branch to $Remote/$Branch..."
& git checkout -B $Branch "$Remote/$Branch" | Out-Host
if ($LASTEXITCODE -ne 0) { Write-Error "git checkout -B failed."; exit $LASTEXITCODE }

& git branch --set-upstream-to="$Remote/$Branch" $Branch | Out-Host
if ($LASTEXITCODE -ne 0) { Write-Error "git branch --set-upstream-to failed."; exit $LASTEXITCODE }

if ($Clean) {
  $cleanArgs = @('-f','-d')
  if ($CleanIgnored) { $cleanArgs += '-x' }
  Write-Host "[Sync] Cleaning untracked files (git clean $($cleanArgs -join ' '))..."
  & git clean @cleanArgs | Out-Host
  if ($LASTEXITCODE -ne 0) { Write-Error "git clean failed."; exit $LASTEXITCODE }
}

$b = git rev-parse --abbrev-ref HEAD
$h = git rev-parse --short HEAD
Write-Host "[Sync] Done. On branch $b at $h"

