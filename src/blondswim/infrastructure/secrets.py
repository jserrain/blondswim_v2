import os
from pathlib import Path

from dotenv import load_dotenv


def anthropic_api_key() -> str:
    """Retorna la clau: primer ANTHROPIC_API_KEY, si no, el fitxer de ANTHROPIC_API_KEY_FILE."""
    load_dotenv()
    if key := os.getenv("ANTHROPIC_API_KEY"):
        return key.strip()
    path = os.getenv("ANTHROPIC_API_KEY_FILE")
    if not path:
        raise RuntimeError("Defineix ANTHROPIC_API_KEY o ANTHROPIC_API_KEY_FILE a .env")
    return Path(path).expanduser().read_text().strip()
