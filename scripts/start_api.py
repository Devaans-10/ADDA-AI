"""Start the canonical local demo API on 127.0.0.1:8000.

Loads nonempty values from services/api/.env, then from a sibling
outputs/nexusai/services/api/.env if Search is still unconfigured.
Never prints environment values.
"""
from pathlib import Path
import os

from dotenv import dotenv_values
import uvicorn

MVP_ROOT = Path(__file__).resolve().parents[1]
API_DIR = MVP_ROOT / 'services' / 'api'
ENV_CANDIDATES = [
    API_DIR / '.env',
    MVP_ROOT.parent / 'nexusai' / 'services' / 'api' / '.env',
]


def apply_nonempty(path: Path) -> None:
    if not path.exists():
        return
    for key, value in dotenv_values(path).items():
        if not value or not str(value).strip():
            continue
        current = os.environ.get(key, '')
        if key == 'TAVILY_API_KEY' or not str(current).strip():
            os.environ[key] = str(value).strip()


def main() -> None:
    os.environ.setdefault('NEXUS_PROVIDER', 'demo')
    os.environ.setdefault('DOCUMENT_ENABLED', 'true')
    os.environ.setdefault(
        'ALLOWED_ORIGINS',
        'http://localhost:3000,http://127.0.0.1:3000',
    )
    os.environ.setdefault('DEMO_ACCESS_TOKEN', '')
    for path in ENV_CANDIDATES:
        apply_nonempty(path)
    uvicorn.run('app.main:app', app_dir=str(API_DIR), host='127.0.0.1', port=8000, reload=False)


if __name__ == '__main__':
    main()
