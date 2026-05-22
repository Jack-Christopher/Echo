"""List and log detected audio input/output devices."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def log_audio_devices() -> None:
    """Print microphones and speakers to the terminal at startup."""
    try:
        import sounddevice as sd
    except ImportError as e:
        print("[Echo] sounddevice no instalado:", e)
        return

    print("\n" + "=" * 60)
    print("  Echo - dispositivos de audio detectados")
    print("=" * 60)

    default_in, default_out = sd.default.device
    print(f"\n  Por defecto -> entrada: {default_in}  |  salida: {default_out}\n")

    devices = sd.query_devices()
    inputs = []
    outputs = []

    for i, dev in enumerate(devices):
        name = dev.get("name", "?")
        max_in = dev.get("max_input_channels", 0)
        max_out = dev.get("max_output_channels", 0)
        if max_in > 0:
            mark = " * DEFAULT" if i == default_in else ""
            inputs.append(f"  [{i}] {name} ({max_in} canales entrada){mark}")
        if max_out > 0:
            mark = " * DEFAULT" if i == default_out else ""
            outputs.append(f"  [{i}] {name} ({max_out} canales salida){mark}")

    print("  Micrófonos (entrada):")
    if inputs:
        print("\n".join(inputs))
    else:
        print("    (ninguno detectado)")

    print("\n  Parlantes / auriculares (salida):")
    if outputs:
        print("\n".join(outputs))
    else:
        print("    (ninguno detectado)")

    print("\n" + "=" * 60 + "\n")
    logger.info(
        "Audio defaults: input=%s output=%s (%d devices)",
        default_in,
        default_out,
        len(devices),
    )
