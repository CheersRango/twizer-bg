param(
    [string]$PluginDir = ".",
    [string]$TargetUrl = "https://api.twizer.xyz"
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n==== $msg ====" -ForegroundColor Cyan }
function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Gray }
function Write-Ok($msg)   { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR]  $msg" -ForegroundColor Red }

# Normalize and validate plugin directory
$PluginDir = (Resolve-Path -LiteralPath $PluginDir).Path
Write-Info "Plugin klasoru: $PluginDir"

# Basic manifest check
$manifestPath = Join-Path $PluginDir "manifest.json"
if (-not (Test-Path -LiteralPath $manifestPath)) {
    Write-Err "manifest.json bulunamadi. Dogru klasorde misiniz?"
    exit 1
}
Write-Ok "manifest.json bulundu."

# Files to scan
$extensions = @("*.js", "*.ts", "*.tsx", "*.jsx", "*.html")
$patterns = @(
    "https://api.twizer.xyz",
    "https://api.twizer.xyz",
    "https://api.twizer.xyz",
    "https://api.twizer.xyz"
)

Write-Step "URL'ler taraniyor ve guncelleniyor"
$changedFiles = @()

Get-ChildItem -LiteralPath $PluginDir -Recurse -File -Include $extensions | ForEach-Object {
    $path = $_.FullName
    $content = Get-Content -LiteralPath $path -Raw
    $newContent = $content

    foreach ($pattern in $patterns) {
        $newContent = $newContent -replace [regex]::Escape($pattern), $TargetUrl
    }

    if ($newContent -ne $content) {
        Set-Content -LiteralPath $path -Value $newContent -Encoding UTF8
        $changedFiles += $path
        Write-Ok "Guncellendi: $path"
    }
}

if ($changedFiles.Count -eq 0) {
    Write-Warn "Degistirilecek localhost/127.0.0.1 URL bulunamadi. Devam ediliyor."
}

# Optional build step if package.json exists
$packageJson = Join-Path $PluginDir "package.json"
if (Test-Path -LiteralPath $packageJson) {
    Write-Step "package.json bulundu. npm install + npm run build deneniyor"
    Push-Location $PluginDir
    try {
        if (Test-Path -LiteralPath "package-lock.json" -or Test-Path -LiteralPath "package.json") {
            npm install
        }
        npm run build
        Write-Ok "npm build tamamlandi."
    } catch {
        Write-Warn "npm adimlari hata verdi: $($_.Exception.Message)"
    } finally {
        Pop-Location
    }
} else {
    Write-Info "package.json bulunamadi; build adimi atlandi (muhtemelen duz JS plugin)."
}

Write-Step "Islem tamam"
Write-Host "Degisen dosyalar: $($changedFiles.Count)" -ForegroundColor Cyan
Write-Host "Figma'da yeniden import etmeyi unutmayin: Plugins > Development > Import plugin from manifest..." -ForegroundColor Gray




