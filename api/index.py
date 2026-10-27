"""Vercel entrypoint: the FastAPI app from server.py serves /api/*; web/ is served by Vercel's CDN."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from server import app  # noqa: E402,F401
