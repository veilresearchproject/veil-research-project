"""Validate public Research Library metadata and local PDF links before release."""
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[2]
SCHEMA = REPO / "docs/research-library/case-schema.json"


def date_value(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"Duplicate JSON key: {key}.")
        obj[key] = value
    return obj


def validate_catalog(catalog):
    content = json.loads(catalog.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if not isinstance(content, dict) or set(content) != set(schema["required"]):
        raise ValueError("Catalog must contain schema_version, last_updated and cases only.")
    if content["schema_version"] != schema["properties"]["schema_version"]["const"]:
        raise ValueError("Unsupported catalog schema version.")
    if not date_value(content["last_updated"]) or not isinstance(content["cases"], list):
        raise ValueError("Invalid catalog date or case list.")
    case_schema = schema["properties"]["cases"]["items"]
    required = set(case_schema["required"])
    fields = case_schema["properties"]
    library = catalog.resolve().parent
    ids = set()
    paths = set()
    for index, record in enumerate(content["cases"], 1):
        try:
            validate_entry(record, required, fields, library, content["last_updated"], ids, paths)
        except (ValueError, OSError) as exc:
            raise ValueError(f"Catalog entry {index}: {exc}") from exc
    return len(ids)


def validate_entry(record, required, fields, library, last_updated, ids, paths):
    if not isinstance(record, dict) or not required <= set(record) <= fields.keys():
        raise ValueError("Missing or unexpected fields.")
    case_id = record["id"]
    if not isinstance(case_id, str) or not re.fullmatch(fields["id"]["pattern"], case_id) or case_id in ids:
        raise ValueError("Invalid or duplicate case ID.")
    if record["status"] != fields["status"]["const"] or record["classification"] not in fields["classification"]["enum"]:
        raise ValueError("A published status and a recognized finding are required.")
    for key in ("event_date", "publication_date"):
        if not date_value(record[key]):
            raise ValueError(f"Invalid {key}.")
    if not record["event_date"] <= record["publication_date"] <= last_updated:
        raise ValueError("Event, publication and catalog dates are out of order.")
    for key in ("title", "summary", "review_version"):
        if key in record and (not isinstance(record[key], str) or not record[key].strip()):
            raise ValueError(f"{key} must contain text.")
    if len(record["summary"]) > fields["summary"]["maxLength"]:
        raise ValueError("Summary exceeds its length limit.")
    topics = record.get("topics", [])
    if not isinstance(topics, list) or any(not isinstance(topic, str) or not topic.strip() for topic in topics):
        raise ValueError("Topics must be a list of nonempty strings.")
    url = record["report_url"]
    if not isinstance(url, str) or not re.fullmatch(fields["report_url"]["pattern"], url):
        raise ValueError("Report URL must be a relative PDF path.")
    target = library / url
    if not target.is_file() or target.resolve() != target:
        raise ValueError("Report PDF must be a local file without symlinks.")
    if url.casefold() in paths:
        raise ValueError("Report PDF already belongs to another catalog entry.")
    with target.open("rb") as report:
        if report.read(5) != b"%PDF-":
            raise ValueError("Report file does not start with a PDF header.")
    ids.add(case_id)
    paths.add(url.casefold())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", type=Path, nargs="?", default=REPO / "research-library/cases.json")
    args = parser.parse_args()
    try:
        count = validate_catalog(args.catalog)
    except (ValueError, OSError) as exc:
        parser.exit(1, f"Catalog: {exc}\n")
    print(f"Catalog validated: {count} published case(s).")


if __name__ == "__main__":
    main()
