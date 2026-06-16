"""Import bird encyclopedia data from a JSON export.

Usage:
    py -3.12 scripts/import_birds_json.py "D:\\path\\to\\birds.json"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal, init_db
from app.models import Bird


def pick_image(item: dict) -> str:
    return item.get("image_url") or item.get("image_thumb") or ""


def normalize_bird(item: dict) -> Bird:
    name = item.get("common_name_cn") or item.get("common_name") or item.get("scientific_name") or ""
    latin_name = item.get("scientific_name") or ""
    description = item.get("description_cn") or item.get("description") or ""
    search_count = item.get("observations_count") or 0

    return Bird(
        name=str(name)[:100],
        latin_name=str(latin_name)[:200],
        region="",
        habits="",
        description=str(description),
        image_url=pick_image(item)[:255],
        search_count=int(search_count),
    )


def load_items(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected the JSON root to be a list.")
    return [item for item in data if isinstance(item, dict)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_path", type=Path)
    args = parser.parse_args()

    items = load_items(args.json_path)
    birds = [normalize_bird(item) for item in items]

    init_db()
    db = SessionLocal()
    try:
        db.query(Bird).delete()
        db.bulk_save_objects(birds)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"Imported {len(birds)} birds from {args.json_path}")


if __name__ == "__main__":
    main()
