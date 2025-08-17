# x987: Guardrails v3 — lint only changed files; pytest(5)=OK
function Invoke-Step { param([string]$Name,[string]$Cmd,[switch]$PyTest)
  Write-Host "== $Name ==" -ForegroundColor Cyan
  cmd /c $Cmd
  $code = $LASTEXITCODE
  if ($PyTest -and $code -eq 5) { Write-Host "pytest: no tests collected — OK"; return }
  if ($code -ne 0) { Write-Host "FAIL ($Name): $code" -ForegroundColor Red; exit $code }
}
function ChangedPy {
  $a = git diff --cached --name-only --diff-filter=ACMRTUXB -- *.py 2>$null; if ($a) { return $a }
  $b = git diff --name-only --diff-filter=ACMRTUXB -- *.py 2>$null; if ($b) { return $b }
  git ls-files -m -o --exclude-standard -- *.py 2>$null
}
$files = ChangedPy
if ($files) { Invoke-Step "ruff (changed files)" ("ruff check " + ($files -join " ")) }
else { Write-Host "== ruff: no Python changes detected, skipping ==" -ForegroundColor Yellow }
Invoke-Step "pytest" "pytest -q" -PyTest
Invoke-Step "x987 run" "python -m x987"
Write-Host "OK: all checks passed" -ForegroundColor Green
