# Run Business Standard smoke + regression against latest public build, then Excel report.
# Usage (from repo root):  pwsh -File scripts/run_business_standard_build_verification.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

New-Item -ItemType Directory -Force -Path "reports/excel" | Out-Null

$env:BASE_URL = "https://www.business-standard.com"
if (-not $env:PLAYWRIGHT_TIMEOUT_MS) {
    $env:PLAYWRIGHT_TIMEOUT_MS = "90000"
}

Write-Host "== Playwright browsers (Chromium) =="
python -m playwright install chromium

Write-Host "== Business Standard — smoke =="
python -m pytest tests/ -v --tb=short `
    -m "business_standard and smoke and not appium" `
    --junitxml=reports/junit-bs-smoke.xml
$smokeExit = $LASTEXITCODE

Write-Host "== Business Standard — regression =="
python -m pytest tests/ -v --tb=short `
    -m "business_standard and regression and not appium" `
    --junitxml=reports/junit-bs-regression.xml
$regExit = $LASTEXITCODE

Write-Host "== Excel report =="
python -m utils.excel_report

$excel = Join-Path $Root "reports\excel\execution_report.xlsx"
Write-Host "Report: $excel"

if ($smokeExit -ne 0 -or $regExit -ne 0) {
    Write-Warning "One or more pytest runs failed (smoke=$smokeExit regression=$regExit)."
    exit 1
}
