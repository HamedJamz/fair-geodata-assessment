#!/usr/bin/env python3
"""Step 3 (optional) — cross-check a sub-sample with the F-UJI tool.

Needs a local F-UJI server (Docker):
    docker run -d -p 1071:1071 ghcr.io/pangaea-data-publisher/fuji
F-UJI inspects the landing page and the data links, so it is slow (about
10-60 s per dataset). Results are cached per DOI; the script can be resumed.
"""
import argparse, json, sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fairgeo.common import RAW, RESULTS, load_config


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-repository", type=int, default=10)
    args = ap.parse_args()
    cfg = load_config()["fuji"]
    table = pd.read_csv(RESULTS / "fair_assessment_table.csv")
    sub = table.groupby("client_id", sort=False).head(args.per_repository)
    cache = RAW / "fuji"
    cache.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, r in enumerate(sub.itertuples(), 1):
        f = cache / (r.doi.replace("/", "_") + ".json")
        if not f.exists():
            try:
                resp = requests.post(cfg["url"], auth=(cfg["username"], cfg["password"]), timeout=600,
                                     json={"object_identifier": f"https://doi.org/{r.doi}",
                                           "test_debug": False, "use_datacite": True})
                resp.raise_for_status()
            except requests.ConnectionError:
                sys.exit("F-UJI server not reachable at " + cfg["url"] + " — start the container first.")
            except requests.RequestException as e:
                print(f"[{i}/{len(sub)}] {r.doi}: failed ({e})"); continue
            f.write_text(resp.text)
        pct = (json.loads(f.read_text()).get("summary") or {}).get("score_percent") or {}
        rows.append({"doi": r.doi, "client_id": r.client_id,
                     **{f"fuji_{k}": pct.get(k) for k in ("F", "A", "I", "R", "FAIR")}})
        print(f"[{i}/{len(sub)}] {r.doi}: F-UJI FAIR = {pct.get('FAIR')}")
    pd.DataFrame(rows).to_csv(RESULTS / "fuji_scores.csv", index=False)
    print("-> results/fuji_scores.csv")


if __name__ == "__main__":
    main()
