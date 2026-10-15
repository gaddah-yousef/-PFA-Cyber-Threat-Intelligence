"""Point d'entrée compatible avec la commande ``uvicorn main:app``."""

from app.main import app

__all__ = ["app"]
