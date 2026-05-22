# Echo setup: download Whisper.cpp + Piper (Windows x64) into models/
param(
    [switch]$Force,
    [switch]$SkipWhisper,
    [switch]$SkipPiper
)

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Models = Join-Path $Root "models"

$WhisperVersion = "v1.8.4"
$WhisperZip = "whisper-bin-x64.zip"
$WhisperUrl = "https://github.com/ggml-org/whisper.cpp/releases/download/$WhisperVersion/$WhisperZip"
$WhisperModelBase = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
$WhisperModels = @(
    @{ File = "ggml-small.bin"; Note = "recomendado para comandos en espanol" },
    @{ File = "ggml-base.bin"; Note = "reserva rapida" }
)
$WhisperDlls = @("whisper-cli.exe", "whisper.dll", "ggml.dll", "ggml-base.dll", "ggml-cpu.dll")

$PiperVersion = "2023.11.14-2"
$PiperZip = "piper_windows_amd64.zip"
$PiperUrl = "https://github.com/rhasspy/piper/releases/download/$PiperVersion/$PiperZip"
$PiperVoiceBase = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium"
$PiperVoiceFiles = @("es_ES-davefx-medium.onnx", "es_ES-davefx-medium.onnx.json")

function Write-Step([string]$Message) {
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Ensure-Dir([string]$Path) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

function Download-File([string]$Url, [string]$Dest, [switch]$SkipIfExists) {
    if ($SkipIfExists -and (Test-Path $Dest) -and -not $Force) {
        Write-Host "  OK (ya existe): $(Split-Path $Dest -Leaf)"
        return
    }
    $name = Split-Path $Dest -Leaf
    Write-Host "  Descargando $name ..."
    Invoke-WebRequest -Uri $Url -OutFile $Dest -UseBasicParsing
}

function Expand-Zip([string]$ZipPath, [string]$DestDir) {
    if (Test-Path $DestDir) {
        Remove-Item $DestDir -Recurse -Force
    }
    Expand-Archive -Path $ZipPath -DestinationPath $DestDir -Force
}

function Test-WhisperReady([string]$Dir) {
    $cli = Test-Path (Join-Path $Dir "whisper-cli.exe")
    $small = Test-Path (Join-Path $Dir "ggml-small.bin")
    $base = Test-Path (Join-Path $Dir "ggml-base.bin")
    return $cli -and ($small -or $base)
}

function Test-PiperReady([string]$Dir) {
    (Test-Path (Join-Path $Dir "piper.exe")) -and (Test-Path (Join-Path $Dir "es_ES-davefx-medium.onnx"))
}

Write-Step "Echo setup - modelos offline (Whisper + Piper)"
Ensure-Dir (Join-Path $Models "whisper")
Ensure-Dir (Join-Path $Models "piper")

if (-not $SkipWhisper) {
    Write-Step "Whisper.cpp $WhisperVersion"
    $whisperDir = Join-Path $Models "whisper"
    $tmp = Join-Path $env:TEMP "echo-setup-whisper"
    Ensure-Dir $tmp

    if (-not (Test-WhisperReady $whisperDir) -or $Force) {
        $zipPath = Join-Path $tmp $WhisperZip
        Download-File $WhisperUrl $zipPath
        $extract = Join-Path $tmp "extract"
        Expand-Zip $zipPath $extract
        $release = Join-Path $extract "Release"
        if (-not (Test-Path $release)) {
            throw "No se encontro carpeta Release en $WhisperZip"
        }
        foreach ($file in $WhisperDlls) {
            $src = Join-Path $release $file
            if (-not (Test-Path $src)) {
                throw "Falta en el zip: $file"
            }
            Copy-Item $src -Destination $whisperDir -Force
        }
        Write-Host "  Binarios copiados a models/whisper/"
    } else {
        Write-Host "  Binarios Whisper ya presentes."
    }

    foreach ($m in $WhisperModels) {
        $dest = Join-Path $whisperDir $m.File
        $url = "$WhisperModelBase/$($m.File)"
        Write-Host "  Modelo $($m.File) ($($m.Note))"
        Download-File $url $dest -SkipIfExists
    }
}

if (-not $SkipPiper) {
    Write-Step "Piper TTS $PiperVersion"
    $piperDir = Join-Path $Models "piper"
    $tmp = Join-Path $env:TEMP "echo-setup-piper"
    Ensure-Dir $tmp

    if (-not (Test-Path (Join-Path $piperDir "piper.exe")) -or $Force) {
        $zipPath = Join-Path $tmp $PiperZip
        Download-File $PiperUrl $zipPath
        $extract = Join-Path $tmp "extract"
        Expand-Zip $zipPath $extract
        $piperSrc = Join-Path $extract "piper"
        if (-not (Test-Path $piperSrc)) {
            throw "No se encontro carpeta piper en $PiperZip"
        }
        Copy-Item (Join-Path $piperSrc "*") -Destination $piperDir -Recurse -Force
        Write-Host "  Piper copiado a models/piper/"
    } else {
        Write-Host "  Piper ya presente."
    }

    foreach ($voice in $PiperVoiceFiles) {
        Download-File "$PiperVoiceBase/$voice" (Join-Path $piperDir $voice) -SkipIfExists
    }
}

Write-Step "Comprobacion"
$whisperOk = Test-WhisperReady (Join-Path $Models "whisper")
$piperOk = Test-PiperReady (Join-Path $Models "piper")
Write-Host "  Whisper: $(if ($whisperOk) { 'OK' } else { 'FALTA' })"
Write-Host "  Piper:   $(if ($piperOk) { 'OK' } else { 'FALTA' })"

if (-not $whisperOk) {
    throw "Whisper incompleto. Reintenta: .\setup.ps1 -Force"
}
if (-not (Test-Path (Join-Path $Models "whisper\ggml-small.bin"))) {
    Write-Warning "Falta ggml-small.bin (mejor precision). Vuelve a ejecutar setup.ps1."
}
if (-not $piperOk) {
    Write-Warning "Piper incompleto (voz opcional). Reintenta: .\setup.ps1 -Force"
}

Write-Host ""
Write-Host 'Listo. Ejecuta: .\run_echo.bat' -ForegroundColor Green
