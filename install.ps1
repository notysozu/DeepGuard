[CmdletBinding()]
param(
    [string]$RepoUrl = $env:REPO_URL,
    [string]$RepoDir = $(if ($env:REPO_DIR) { $env:REPO_DIR } else { "DeepGuard" })
)

$ErrorActionPreference = "Stop"
$ScriptName = Split-Path -Leaf $PSCommandPath
if (-not $ScriptName) {
    $ScriptName = "install.ps1"
}

function Write-Log {
    param([string]$Message)
    Write-Host "[$ScriptName] $Message"
}

function Write-Warn {
    param([string]$Message)
    Write-Warning "[$ScriptName] $Message"
}

function Fail {
    param([string]$Message)
    throw "[$ScriptName] $Message"
}

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-SystemDependencies {
    if (Test-Command "winget") {
        $packages = @(
            "Git.Git",
            "Python.Python.3.11",
            "OpenJS.NodeJS.LTS"
        )

        foreach ($package in $packages) {
            $existing = winget list --id $package --exact --accept-source-agreements 2>$null
            if ($LASTEXITCODE -eq 0 -and $existing) {
                Write-Log "$package is already installed"
                continue
            }

            Write-Log "Installing $package via winget"
            winget install --id $package --source winget --silent --accept-package-agreements --accept-source-agreements --exact | Out-Null
        }
        return
    }

    if (Test-Command "choco") {
        Write-Log "Installing Git, Python, and Node.js via Chocolatey"
        choco install -y git python nodejs-lts | Out-Null
        return
    }

    Fail "Neither winget nor choco is available. Install Git, Python 3.10+, and Node.js 18+ manually."
}

function Ensure-BaseTools {
    $missing = @()
    foreach ($tool in @("git", "python", "node", "npm")) {
        if (-not (Test-Command $tool)) {
            $missing += $tool
        }
    }

    if ($missing.Count -gt 0) {
        Write-Log "Installing missing system dependencies: $($missing -join ', ')"
        Install-SystemDependencies
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    }

    foreach ($tool in @("git", "python", "node", "npm")) {
        if (-not (Test-Command $tool)) {
            Fail "$tool is required but was not found after installation."
        }
    }
}

function Resolve-RepoDir {
    $cwd = (Get-Location).Path
    if ((Test-Path (Join-Path $cwd "requirements.txt")) -and (Test-Path (Join-Path $cwd "web_ui/package.json"))) {
        return $cwd
    }

    $target = Join-Path $cwd $RepoDir
    if (Test-Path (Join-Path $target ".git")) {
        return $target
    }

    if (-not $RepoUrl -or $RepoUrl -eq "<YOUR_REPO_URL>") {
        Fail "Set REPO_URL before running the installer outside an existing checkout."
    }

    Write-Log "Cloning repository into $target"
    git clone $RepoUrl $target | Out-Null
    return $target
}

function Set-EnvValue {
    param(
        [string]$Path,
        [string]$Key,
        [string]$Value
    )

    $content = @()
    if (Test-Path $Path) {
        $content = Get-Content -Path $Path
    }

    $updated = New-Object System.Collections.Generic.List[string]
    $replaced = $false

    foreach ($line in $content) {
        if ($line.StartsWith("$Key=")) {
            $updated.Add("$Key=$Value")
            $replaced = $true
        }
        else {
            $updated.Add($line)
        }
    }

    if (-not $replaced) {
        $updated.Add("$Key=$Value")
    }

    Set-Content -Path $Path -Value $updated -Encoding utf8
}

function Prepare-EnvFiles {
    param([string]$RepoPath)

    $envExample = Join-Path $RepoPath ".env.example"
    $envFile = Join-Path $RepoPath ".env"
    if (-not (Test-Path $envExample)) {
        Fail "Missing .env.example in $RepoPath"
    }

    if (-not (Test-Path $envFile)) {
        Copy-Item $envExample $envFile
    }
    else {
        Write-Log "Reusing existing .env"
    }

    $modelsLocal = @"
models:
  - name: model_a
    url: http://127.0.0.1:8001/predict
  - name: model_b
    url: http://127.0.0.1:8002/predict
"@
    Set-Content -Path (Join-Path $RepoPath "configs/models.local.yaml") -Value $modelsLocal -Encoding utf8

    Set-EnvValue -Path $envFile -Key "MODEL_REGISTRY_PATH" -Value "configs/models.local.yaml"
    Set-EnvValue -Path $envFile -Key "API_PORT" -Value "8000"
    Set-EnvValue -Path $envFile -Key "MODEL_A_PORT" -Value "8001"
    Set-EnvValue -Path $envFile -Key "MODEL_B_PORT" -Value "8002"

    Set-Content -Path (Join-Path $RepoPath "web_ui/.env.local") -Value "VITE_API_BASE=http://127.0.0.1:8000" -Encoding utf8
}

function Install-ProjectDependencies {
    param([string]$RepoPath)

    $venvPath = Join-Path $RepoPath ".venv"
    if (-not (Test-Path $venvPath)) {
        Write-Log "Creating Python virtual environment"
        python -m venv $venvPath
    }

    $pythonExe = Join-Path $RepoPath ".venv/Scripts/python.exe"
    if (-not (Test-Path $pythonExe)) {
        Fail "Virtual environment Python executable was not created."
    }

    & $pythonExe -m pip install --upgrade pip
    & $pythonExe -m pip install -r (Join-Path $RepoPath "requirements.txt")

    if (Test-Path (Join-Path $RepoPath "web_ui/package-lock.json")) {
        npm --prefix (Join-Path $RepoPath "web_ui") ci
    }
    else {
        npm --prefix (Join-Path $RepoPath "web_ui") install
    }

    npm --prefix (Join-Path $RepoPath "web_ui") run build
}

function Start-ServiceProcess {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$LogPath,
        [string]$PidPath
    )

    if (Test-Path $PidPath) {
        $existingPid = (Get-Content $PidPath -ErrorAction SilentlyContinue | Select-Object -First 1)
        if ($existingPid -and (Get-Process -Id $existingPid -ErrorAction SilentlyContinue)) {
            Write-Log "$Name is already running with PID $existingPid"
            return
        }
    }

    $errorLogPath = [System.IO.Path]::ChangeExtension($LogPath, ".err.log")

    $process = Start-Process -FilePath $FilePath `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $LogPath `
        -RedirectStandardError $errorLogPath `
        -PassThru `
        -WindowStyle Hidden

    Set-Content -Path $PidPath -Value $process.Id -Encoding ascii
    Write-Log "Started $Name with PID $($process.Id)"
}

function Wait-ForHealth {
    param([string]$Url)

    for ($i = 0; $i -lt 30; $i++) {
        try {
            Invoke-RestMethod -Uri $Url -Method Get | Out-Null
            Write-Log "Health check passed: $Url"
            return
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }

    Write-Warn "Health check did not pass in time: $Url"
}

function Start-Application {
    param([string]$RepoPath)

    $runtimeDir = Join-Path $RepoPath ".deepguard"
    $logDir = Join-Path $runtimeDir "logs"
    $pidDir = Join-Path $runtimeDir "pids"
    New-Item -ItemType Directory -Force -Path $logDir, $pidDir | Out-Null

    $pythonExe = Join-Path $RepoPath ".venv/Scripts/python.exe"
    $uvicornExe = Join-Path $RepoPath ".venv/Scripts/uvicorn.exe"
    if (-not (Test-Path $uvicornExe)) {
        Fail "uvicorn executable was not found in the virtual environment."
    }

    $envMap = @{
        "PYTHONPATH"   = $RepoPath
        "API_PORT"     = "8000"
        "MODEL_A_PORT" = "8001"
        "MODEL_B_PORT" = "8002"
    }

    Push-Location $RepoPath
    try {
        & $pythonExe "scripts/migrate.py"

        foreach ($entry in $envMap.GetEnumerator()) {
            [System.Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, "Process")
        }

        Start-ServiceProcess -Name "model_a" `
            -FilePath $uvicornExe `
            -Arguments @("model_services.model_a.app.main:app", "--host", "127.0.0.1", "--port", "8001") `
            -WorkingDirectory $RepoPath `
            -LogPath (Join-Path $logDir "model_a.log") `
            -PidPath (Join-Path $pidDir "model_a.pid")

        Start-ServiceProcess -Name "model_b" `
            -FilePath $uvicornExe `
            -Arguments @("model_services.model_b.app.main:app", "--host", "127.0.0.1", "--port", "8002") `
            -WorkingDirectory $RepoPath `
            -LogPath (Join-Path $logDir "model_b.log") `
            -PidPath (Join-Path $pidDir "model_b.pid")

        Start-ServiceProcess -Name "api_gateway" `
            -FilePath $uvicornExe `
            -Arguments @("api_gateway.app.main:app", "--host", "127.0.0.1", "--port", "8000") `
            -WorkingDirectory $RepoPath `
            -LogPath (Join-Path $logDir "api_gateway.log") `
            -PidPath (Join-Path $pidDir "api_gateway.pid")

        Start-ServiceProcess -Name "web_ui" `
            -FilePath "npm.cmd" `
            -Arguments @("--prefix", (Join-Path $RepoPath "web_ui"), "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
            -WorkingDirectory $RepoPath `
            -LogPath (Join-Path $logDir "web_ui.log") `
            -PidPath (Join-Path $pidDir "web_ui.pid")
    }
    finally {
        Pop-Location
    }

    Wait-ForHealth -Url "http://127.0.0.1:8000/health"
}

Ensure-BaseTools
$RepoPath = Resolve-RepoDir
Prepare-EnvFiles -RepoPath $RepoPath
Install-ProjectDependencies -RepoPath $RepoPath
Start-Application -RepoPath $RepoPath

Write-Host ""
Write-Host "DeepGuard is ready."
Write-Host "API: http://127.0.0.1:8000"
Write-Host "UI: http://127.0.0.1:5173"
Write-Host "Logs: $(Join-Path $RepoPath '.deepguard/logs')"
Write-Host "PIDs: $(Join-Path $RepoPath '.deepguard/pids')"
Write-Host ""
Write-Host "Security note: review this script before using iwr|iex in shared or production environments."
