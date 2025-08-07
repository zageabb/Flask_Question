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
        name = data.get("id", file.stem)
        templates[name] = data
    return templates
