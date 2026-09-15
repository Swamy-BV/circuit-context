"""Load the versioned catalogue and its separately maintained topic collections."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

from .models import Corpus

_COLLECTIONS = (
    "general.json", "two_layer.json", "emc.json", "interfaces.json", "mechanical.json",
    "gpio.json", "uart.json", "spi.json", "i2c.json",
    "usb_c.json", "usb_c_layout.json", "usb_pd.json", "four_layer.json",
    "pcb_calculations.json",
    "serial_flash.json", "sdmmc.json", "digital_audio.json", "debug.json",
)


@lru_cache(maxsize=1)
def load() -> tuple[Corpus, str]:
    """Validate all records together and fingerprint every packaged input."""
    root = Path(__file__).with_name("data")
    digest = hashlib.sha256()

    def read(name: str) -> object:
        raw = (root / name).read_bytes()
        digest.update(name.encode() + b"\0" + len(raw).to_bytes(8, "big") + raw)
        return json.loads(raw)

    metadata = read("sources.json")
    if not isinstance(metadata, dict):
        raise ValueError("sources.json must contain version and source records")
    guidelines = []
    for name in _COLLECTIONS:
        records = read(name)
        if not isinstance(records, list):
            raise ValueError(f"{name} must contain a list of guidance records")
        guidelines.extend(records)
    corpus = Corpus.model_validate({**metadata, "guidelines": guidelines})
    return corpus, digest.hexdigest()
