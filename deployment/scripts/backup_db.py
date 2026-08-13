#!/usr/bin/env python3
"""Daily MongoDB backup for TruthLens AI.

Exports every collection in the configured database to a timestamped directory
as BSON-extended JSON. Run from the backend venv (has pymongo), e.g.:

    python deployment/scripts/backup_db.py --out ./deployment/backups

Connection string is read from DATABASE_URL or MONGODB_URI (defaults to the
local instance). The script refuses to run against placeholder URIs and never
prints credentials.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from bson import json_util
from pymongo import MongoClient

PLACEHOLDER_MARKERS = ("<user>", "<password>", "change-me")


def resolve_uri() -> str:
    uri = os.environ.get("DATABASE_URL") or os.environ.get("MONGODB_URI")
    return uri or "mongodb://localhost:27017"


def is_placeholder(uri: str) -> bool:
    return any(marker in uri for marker in PLACEHOLDER_MARKERS)


def backup(uri: str, db_name: str, out_dir: Path) -> None:
    if is_placeholder(uri):
        sys.exit("Refusing to back up from a placeholder connection string.")
    if not uri.startswith(("mongodb://", "mongodb+srv://")):
        sys.exit("DATABASE_URL must be a mongodb:// or mongodb+srv:// URI.")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = out_dir / f"{db_name}_{stamp}"
    dest.mkdir(parents=True, exist_ok=True)

    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client[db_name]
    manifest: dict = {
        "database": db_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "uri_host": uri.split("@")[-1],
        "collections": {},
    }
    for name in sorted(db.list_collection_names()):
        docs = list(db[name].find({}))
        target = dest / f"{name}.json"
        with open(target, "w", encoding="utf-8") as fh:
            json.dump(docs, fh, default=json_util.default, ensure_ascii=False)
        manifest["collections"][name] = len(docs)
        print(f"  {name}: {len(docs)} docs -> {target.name}")

    with open(dest / "manifest.json", "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, default=str)
    print(f"Backup complete: {dest}")
    client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup the TruthLens database.")
    parser.add_argument("--out", default="./deployment/backups", help="Backup output directory")
    parser.add_argument("--db", default="truthlens", help="Database name")
    args = parser.parse_args()

    backup(resolve_uri(), args.db, Path(args.out))


if __name__ == "__main__":
    start = time.perf_counter()
    main()
    print(f"Elapsed: {time.perf_counter() - start:.1f}s")
