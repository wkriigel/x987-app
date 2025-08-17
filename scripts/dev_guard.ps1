# x987: Guardrails v2 – lint only changed Python files with project config
function Invoke-Step {
  param([string]$Name,[string]$Cmd)
  Write-Host "== $Name ==" -ForegroundColor Cyan
  cmd /c $Cmd
  if ($LASTEXITCODE -ne 0) {
    Write-Host "FAIL ($Name): $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
  }
}

function Get-ChangedPy {
  $staged = git diff --cached --name-only --diff-filter=ACMRTUXB -- *.py 2>$null
  if ($staged) { return $staged }
  $local  = git diff --name-only --diff-filter=ACMRTUXB -- *.py 2>$null
  if ($local)  { return $local }
  $loose  = git ls-files -m -o --exclude-standard -- *.py 2>$null
  return $loose
}

# 1) Ruff on changed files only (uses .ruff.toml; no extra flags)
$files = Get-ChangedPy
if ($files -and $files.Count -gt 0) {
  Invoke-Step "ruff (changed files)" ("ruff check " + ($files -join " "))
} else {
  Write-Host "== ruff: no Python changes detected, skipping ==" -ForegroundColor Yellow
}

# 2) Tests
Invoke-Step "pytest" "pytest -q"

# 3) Runtime smoke
Invoke-Step "x987 run" "python -m x987"

Write-Host "OK: all checks passed" -ForegroundColor Green
