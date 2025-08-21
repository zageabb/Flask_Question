import json
from pathlib import Path

def load_templates() -> dict[str, dict]:
    """Load JSON form templates from the `forms/` directory."""
    templates: dict[str, dict] = {}
    base = Path(__file__).parent / "forms"
    for file in base.glob("*.json"):
        try:
            data = json.loads(file.read_text())
        except json.JSONDecodeError:
            continue

        # Prefer explicit identifiers but fall back to the filename
        name = data.get("id") or data.get("name") or file.stem

        # Stash the source path so callers can map back to disk even if the
        # template's `id` differs from the file name.
        data["_file"] = file

        templates[name] = data
    return templates
