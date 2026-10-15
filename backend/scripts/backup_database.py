"""Sauvegarde cohérente d'une base SQLite avec rotation simple."""

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def backup_sqlite_database(source: Path, destination: Path, retention: int = 7) -> Path:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Base SQLite introuvable : {source}")
    if retention < 1:
        raise ValueError("La rétention doit être supérieure ou égale à 1")

    destination.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = destination / f"sentinel-pme-{timestamp}.db"
    with sqlite3.connect(source) as source_db, sqlite3.connect(target) as target_db:
        source_db.backup(target_db)

    backups = sorted(destination.glob("sentinel-pme-*.db"), reverse=True)
    for expired in backups[retention:]:
        expired.unlink()
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Chemin de la base SQLite source")
    parser.add_argument("destination", type=Path, help="Dossier de sauvegarde")
    parser.add_argument("--retention", type=int, default=7, help="Nombre de sauvegardes conservées")
    args = parser.parse_args()
    created = backup_sqlite_database(args.source, args.destination, args.retention)
    print(created)


if __name__ == "__main__":
    main()
