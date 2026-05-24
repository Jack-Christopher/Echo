# Echo — Voice Desktop Assistant

Lightweight offline Spanish voice utility for Windows. Controls your browser (Brave, Chrome, Edge, Firefox, Opera) and system actions without AI/LLMs.

## Features (MVP)

- Floating assistant orb + system tray
- Push-to-talk (default: **Win+Space**, or **hold** the blue orb)
- Offline speech recognition (Whisper.cpp) and voice feedback (Piper)
- Browser (configurable): open sites in a new tab, web search, media keys
- Volume, brightness, open Downloads/Documents
- Persistent config in `%LOCALAPPDATA%\Echo\` with project fallback

## Requirements

- Windows 10/11
- Python 3.11+
- A Chromium-based browser or Firefox (Brave, Chrome, Edge, Opera, Firefox)

## Setup

```powershell
cd Echo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
.\setup.ps1
```

`setup.ps1` downloads Whisper.cpp (x64), `ggml-base.bin`, Piper, and the Spanish voice into `models/` (~220 MB total, gitignored). Needs internet once. Re-run with `-Force` to re-download.

## Run

```powershell
.\run_echo.bat
# or
python -m echo.main
```

## Start with Windows

```powershell
.\install_startup.ps1
```

Uses `run_echo_logon.vbs` via Task Scheduler (hidden, no CMD window). Same venv as `run_echo.bat`. Waits 20s after logon and logs to `%LOCALAPPDATA%\Echo\logs\startup-last.log`.

For manual testing: `wscript //nologo run_echo_logon.vbs` or `run_echo_logon.bat`.

Uninstall: `Unregister-ScheduledTask -TaskName "Echo" -Confirm:$false`

## Tests

```powershell
pytest tests/ -v
pytest tests/ -v -m "not smoke"
pytest tests/ -v -m smoke
```

## Config

- Primary: `%LOCALAPPDATA%\Echo\config.json`
- Fallback: `config.json` in project root
- Defaults: `echo/config/defaults.json`

Edit browser, sites, and hotkey in the tray → **Configuracion**. Set **Ruta al navegador** if Brave is not auto-detected (e.g. `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`). Leave empty if detection works. Browser launch debug log: `%LOCALAPPDATA%\Echo\logs\browser-last.log`. To quit: tray → **Salir**, or **right-click the blue orb** → **Salir**.

## Voice commands

See **[COMANDOS.md](COMANDOS.md)** for exact Spanish phrases and terminal output (`[Echo] Texto entendido: "..."`).

## For Dad

1. Hold **Win+Space** (or hold the blue circle), speak, release.
2. Watch the terminal for **Texto entendido**, intent, and result (see COMANDOS.md).
3. Examples: "abre youtube", "busca recetas de pollo", "pausa", "sube volumen".
4. "iniciar dictado" / "terminar dictado" for typing mode.

## License

Private / family use.
