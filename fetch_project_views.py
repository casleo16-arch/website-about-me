import json
import urllib.request
from pathlib import Path

PROJECT_IDS = [
    "964324085",
    "865951583",
    "794262893",
    "894071529",
    "808201366",
    "795320078",
    "798648038",
    "628733977",
]


def fetch_project_views(project_ids):
    views_by_id = {}
    for project_id in project_ids:
        url = f"https://api.scratch.mit.edu/projects/{project_id}"
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = json.load(response)
            views = int(data.get("stats", {}).get("views", 0) or 0)
            views_by_id[project_id] = views
        except Exception:
            views_by_id[project_id] = 0
    return views_by_id


def main():
    output_path = Path(__file__).resolve().parent / "project_views.json"
    views_by_id = fetch_project_views(PROJECT_IDS)
    output_path.write_text(json.dumps(views_by_id, indent=2), encoding="utf-8")
    print(json.dumps(views_by_id, indent=2))


if __name__ == "__main__":
    main()
