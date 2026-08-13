#!/usr/bin/env python3
"""Restore a TruthLens AI MongoDB backup created by backup_db.py.

Usage:
    python deployment/scripts/restore_db.py --backup ./deployment/backups/truthlens_20260812_000000

Restores all collections described in the backup manifest. Pass --drop to
remove existing data in the target database first. The script refuses to run
against placeholder URIs and never prints credentials.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from bson import json_util
from pymongo import MongoClient

PLACEHOLDER_MARKERS = ("<user>", "<password>", "change-me")


def resolve_uri() -> str:
    uri = os.environ.get("DATABASE_URL") or os.environ.get("MONGODB_URI")
    return uri or "mongodb://localhost:27017"


def restore(uri: str, backup_dir: Path, db_name: str, drop: bool) -> None:
    if any(marker in uri for marker in PLACEHOLDER_MARKERS):
        sys.exit("Refusing to restore into a placeholder connection string.")

    manifest_path = backup_dir / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"manifest.json not found in {backup_dir}")
    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)

    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client[db_name]

    for name in sorted(manifest["collections"]):
        source = backup_dir / f"{name}.json"
        if not source.exists():
            print(f"  SKIP {name}: {source.name} not found in backup")
            continue
        with open(source, encoding="utf-8") as fh:
            docs = json.load(fh, object_hook=json_util.object_hook)
        if drop:
            db[name].drop()
        if docs:
            db[name].insert_many(docs)
        print(f"  {name}: restored {len(docs)} docs")

    print(f"Restore complete into database '{db_name}'.")
    client.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore a TruthLens database backup.")
    parser.add_argument("--backup", required=True, help="Backup directory (containing manifest.json)")
    parser.add_argument("--db", default="truthlens", help="Target database name")
    parser.add_argument("--drop", action="store_true", help="Drop existing collections before restoring")
    args = parser.parse_args()

    restore(resolve_uri(), Path(args.backup), args.db, args.drop)


if __name__ == "__main__":
    main()
