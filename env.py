import os
from pathlib import Path


def load_dotenv(path: str | os.PathLike | None = None) -> None:
    p = Path(path) if path else Path(__file__).parent / ".env"
    if not p.exists():
        return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
