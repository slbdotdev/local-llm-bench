import json
from pathlib import Path

HERE = Path(__file__).parent.parent


def text(name):
    return (HERE / "data" / name).read_text(encoding="utf-8")


def merged_catalog():
    rows = []
    for name in ("catalog-0.json", "catalog-1.json", "catalog-2.json", "catalog-3.json",
                 "catalog-4.json", "catalog-5.json", "catalog-6.json"):
        rows.extend(json.loads(text(name)))
    return json.dumps(rows)


def merged_history():
    rows = []
    for year in range(2019, 2028):
        rows.extend(json.loads((HERE / "docs" / "history" / (str(year) + ".json")).read_text(encoding="utf-8")))
    rows.extend(json.loads(text("history-current.json")))
    return json.dumps(rows)
