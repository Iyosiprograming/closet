<#
.SYNOPSIS
    Builds the Closet AI Windows executable.

.DESCRIPTION
    Builds the production React frontend, installs the backend dependencies
    (including PyInstaller) and packages everything into a single executable:

        release\ClosetAI-Windows-x64.exe

    That file is what you attach to a GitHub release. Users only need to
    download it and double-click it — no Python, Node.js or uv required.

.PARAMETER SkipFrontend
    Reuse the existing Frontend\dist build instead of rebuilding it.

.PARAMETER Clean
    Delete packaging\build and packaging\dist before building.

.EXAMPLE
    ./build_windows.ps1
#>

[CmdletBinding()]
param(
    [switch]$SkipFrontend,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = Join-Path $RepoRoot "Frontend"
$BackendDir = Join-Path $RepoRoot "Backend"
$PackagingDir = Join-Path $RepoRoot "packaging"
$BuildDir = Join-Path $PackagingDir "build"
$DistDir = Join-Path $PackagingDir "dist"
$ReleaseDir = Join-Path $RepoRoot "release"
$ReleaseExe = Join-Path $ReleaseDir "ClosetAI-Windows-x64.exe"

function Assert-Command {
    param([string]$Name, [string]$Hint)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "'$Name' was not found on PATH. $Hint"
    }
}

Write-Host "Closet AI — Windows build" -ForegroundColor Cyan
Write-Host "Repository: $RepoRoot"
Write-Host ""

# ---------------------------------------------------------------- frontend
if ($SkipFrontend) {
    Write-Host "[1/4] Frontend build skipped (-SkipFrontend)" -ForegroundColor Yellow
} else {
    Assert-Command -Name "npm" -Hint "Install Node.js 20+ from https://nodejs.org and reopen this shell."

    Write-Host "[1/4] Building the React frontend..." -ForegroundColor Cyan
    Push-Location $FrontendDir

    try {
        if (Test-Path "package-lock.json") {
            npm ci
        } else {
            npm install
        }

        if ($LASTEXITCODE -ne 0) { throw "npm install failed." }

        npm run build

        if ($LASTEXITCODE -ne 0) { throw "npm run build failed." }
    } finally {
        Pop-Location
    }

    Write-Host "      Frontend built into Frontend\dist" -ForegroundColor Green
}

# ----------------------------------------------------------------- backend
Assert-Command -Name "uv" -Hint "Install uv from https://docs.astral.sh/uv and reopen this shell."

Write-Host "[2/4] Syncing backend dependencies (including PyInstaller)..." -ForegroundColor Cyan
Push-Location $BackendDir

try {
    uv sync

    if ($LASTEXITCODE -ne 0) { throw "uv sync failed." }
} finally {
    Pop-Location
}

# -------------------------------------------------------------- executable
if ($Clean) {
    foreach ($dir in @($BuildDir, $DistDir)) {
        if (Test-Path $dir) {
            Write-Host "      Removing $dir" -ForegroundColor Yellow
            Remove-Item -Recurse -Force $dir
        }
    }
}

Write-Host "[3/4] Packaging ClosetAI.exe with PyInstaller (this takes a minute)..." -ForegroundColor Cyan

Push-Location $RepoRoot

try {
    uv run --project $BackendDir pyinstaller `
        --noconfirm `
        --distpath $DistDir `
        --workpath $BuildDir `
        (Join-Path $PackagingDir "ClosetAI.spec")

    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed." }
} finally {
    Pop-Location
}

# ----------------------------------------------------------------- release
Write-Host "[4/4] Copying the executable into release\..." -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null

$BuiltExe = Join-Path $DistDir "ClosetAI.exe"

if (-not (Test-Path $BuiltExe)) {
    throw "PyInstaller did not produce $BuiltExe"
}

Copy-Item -Force $BuiltExe $ReleaseExe

$SizeMb = [math]::Round((Get-Item $ReleaseExe).Length / 1MB, 1)

Write-Host ""
Write-Host "Build complete." -ForegroundColor Green
Write-Host "  Executable : $ReleaseExe ($SizeMb MB)"
Write-Host "  Test it    : run it from any folder, e.g. copy it to the Desktop first."
Write-Host "  User data  : %LOCALAPPDATA%\ClosetAI"
Write-Host "  Publish    : attach release\ClosetAI-Windows-x64.exe to a GitHub release."
