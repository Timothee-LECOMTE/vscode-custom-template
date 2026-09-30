import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THEME_DIR = ROOT / "json_file"


def main():
    settings_files = sorted(THEME_DIR.rglob("settings.json"))
    if not settings_files:
        raise SystemExit(f"Aucun settings.json trouvé dans {THEME_DIR}")

    selected_file = random.choice(settings_files)
    print(f"Thème choisi : {selected_file.parent.name}", file=sys.stderr)
    sys.stdout.write(selected_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
