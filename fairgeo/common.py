from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RESULTS = ROOT / "results"
USER_AGENT = "fair-geodata-assessment/0.1 (student research pilot; python-requests)"


def load_config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())
