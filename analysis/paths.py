"""Path helper: locates exported result files in results/frozen_v2, results/revision or results/derived."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "results" / "derived"; DERIVED.mkdir(parents=True, exist_ok=True)
FIGURES = ROOT / "figures"
DIRS = [ROOT / "results" / "frozen_v2", ROOT / "results" / "revision", DERIVED]
def P(name):
    for d in DIRS:
        if (d / name).exists():
            return str(d / name)
    raise FileNotFoundError(name)
