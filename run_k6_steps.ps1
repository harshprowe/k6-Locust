param(
    [int]$StartRPM = 100,
    [int]$Step = 100,
    [int]$MaxRPM = 2000,
    [string]$Duration = '1m',
    [float]$FailureThresholdPercent = 1.0,
    [string]$ScriptPath = 'k6-login.mjs',
    [string]$OutputPrefix = 'k6-rpm'
)

$pythonExe = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path $pythonExe)) {
    $pythonExe = 'python'
}

$scriptFullPath = Join-Path -Path (Get-Location) -ChildPath $ScriptPath
if (-not (Test-Path $scriptFullPath)) {
    throw "Script not found: $scriptFullPath"
}

$resultsDir = Join-Path -Path (Get-Location) -ChildPath 'results'
if (-not (Test-Path $resultsDir)) { New-Item -ItemType Directory -Path $resultsDir | Out-Null }

for ($rpm = $StartRPM; $rpm -le $MaxRPM; $rpm += $Step) {
    $outJson = Join-Path $resultsDir "$OutputPrefix-$rpm.json"
    Write-Host "Running k6 at $rpm RPM ($([math]::Round($rpm/60,3)) RPS) for $Duration..."

    $env:RPM = $rpm
    $env:DURATION = $Duration
    & k6 run "--summary-export=$outJson" $scriptFullPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "k6 exited with code $LASTEXITCODE. Stopping."
        break
    }

    # parse summary JSON to determine failure rate
    & $pythonExe .\parse_k6_summary.py $outJson $FailureThresholdPercent
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failure threshold exceeded at $rpm RPM. Stopping."
        break
    }
}

Write-Host "Run complete. Results are in: $resultsDir"
