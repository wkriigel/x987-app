param([switch]$RunApp)

function Invoke-Step { param([string]$Name,[string]$Cmd,[switch]$PyTest)
  Write-Host "== $Name ==" -ForegroundColor Cyan
  cmd /c $Cmd
  $code = $LASTEXITCODE
  if ($PyTest -and $code -eq 5) { Write-Host "pytest: no tests collected — OK"; return }
  if ($code -ne 0) { Write-Host "FAIL ($Name): $code" -ForegroundColor Red; exit $code }
}

function ChangedPaths {
  $staged = git diff --cached --name-only --diff-filter=ACMRTUXB 2>$null
  if ($staged) { return $staged }
  $local  = git diff --name-only --diff-filter=ACMRTUXB 2>$null
  if ($local)  { return $local }
  git ls-files -m -o --exclude-standard 2>$null
}

$files = ChangedPaths
$py = $files | Where-Object { $_ -match '\.py$' }
if ($py) { Invoke-Step "ruff (changed files)" ("ruff check " + ($py -join " ")) } else { Write-Host "== ruff: no Python changes detected, skipping ==" -ForegroundColor Yellow }
Invoke-Step "pytest" "pytest -q" -PyTest

$shouldRun = ($files | Where-Object { $_ -match '^x987/scrapers/|^x987/pipeline/|^x987/schema\.py$|^x987/view/' }).Count -gt 0
if ($RunApp -or $shouldRun) { Invoke-Step "x987 run" "python -m x987" } else { Write-Host "== app: skipped (no scraper/pipeline changes) ==" -ForegroundColor Yellow }

Write-Host "OK: guard v4 passed" -ForegroundColor Green
