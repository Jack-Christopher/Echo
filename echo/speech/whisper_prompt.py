"""Initial prompt text to bias Whisper toward Echo command phrases."""

from __future__ import annotations

from echo.config.schema import EchoConfig

_CORE_PHRASES = (
    "Comandos en español de España.",
    "abre youtube abre whatsapp abre gmail",
    "busca pausa reproducir siguiente anterior silencio desilenciar",
    "sube volumen baja volumen sube brillo baja brillo",
    "abre descargas abre documentos",
    "iniciar dictado terminar dictado modo noche",
)


def build_initial_prompt(config: EchoConfig) -> str:
    """Short vocabulary hint for whisper --prompt (improves command recognition)."""
    parts = list(_CORE_PHRASES)
    if config.websites:
        aliases = " ".join(f"abre {k}" for k in sorted(config.websites))
        parts.append(aliases)
    text = " ".join(parts)
    # Whisper prompt length is limited; keep under ~800 chars
    return text[:800]
