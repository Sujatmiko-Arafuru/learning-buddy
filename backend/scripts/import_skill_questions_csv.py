"""
Import skill/tech questions from CSV (docs/skill_questions_full (1).csv)
into the MongoDB collection `current_tech_questions`.

Usage (from backend folder):
    python -m scripts.import_skill_questions_csv "../docs/skill_questions_full (1).csv"
or:
    python scripts/import_skill_questions_csv.py "../docs/skill_questions_full (1).csv"
"""

import csv
import os
import sys
from typing import List, Dict

# Ensure we can import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import collections, db  # noqa: E402


def import_skill_questions(csv_path: str) -> None:
    """Import questions from the given CSV file into current_tech_questions."""
    if db is None or collections.get("current_tech_questions") is None:
        print("[ERROR] Database not connected. Please check your MONGO_URI / DB_NAME.")
        return

    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV file not found: {csv_path}")
        return

    print("=" * 70)
    print("Importing skill questions from CSV")
    print(f"Source file : {csv_path}")
    print(f"Target coll : {db.name}.current_tech_questions")
    print("=" * 70)

    docs: List[Dict] = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        required_cols = {
            "tech_category",
            "difficulty",
            "question_desc",
            "option_1",
            "option_2",
            "option_3",
            "option_4",
            "correct_answer",
        }

        missing = required_cols - set(reader.fieldnames or [])
        if missing:
            print(f"[ERROR] CSV is missing required columns: {', '.join(sorted(missing))}")
            return

        for row in reader:
            # Clean whitespace
            doc = {
                "tech_category": (row.get("tech_category") or "").strip(),
                "difficulty": (row.get("difficulty") or "").strip().lower(),  # store as lower case
                "question_desc": (row.get("question_desc") or "").strip(),
                "option_1": (row.get("option_1") or "").strip(),
                "option_2": (row.get("option_2") or "").strip(),
                "option_3": (row.get("option_3") or "").strip(),
                "option_4": (row.get("option_4") or "").strip(),
                "correct_answer": (row.get("correct_answer") or "").strip(),
            }

            # Skip empty rows
            if not doc["question_desc"]:
                continue

            docs.append(doc)

    coll = collections["current_tech_questions"]

    print(f"[INFO] Parsed {len(docs)} questions from CSV")
    if not docs:
        print("[WARN] No documents to import. Aborting.")
        return

    # Replace existing documents
    result_del = coll.delete_many({})
    print(f"[OK] Deleted {result_del.deleted_count} existing documents from current_tech_questions")

    coll.insert_many(docs)
    print(f"[OK] Inserted {len(docs)} documents into current_tech_questions")
    print("[DONE] Import complete.")


if __name__ == "__main__":
    # If path provided as CLI arg, use that; otherwise default to ../docs/skill_questions_full (1).csv
    if len(sys.argv) >= 2:
        csv_file = sys.argv[1]
    else:
        csv_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "docs",
            "skill_questions_full (1).csv",
        )

    import_skill_questions(csv_file)

