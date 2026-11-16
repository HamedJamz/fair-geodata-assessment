#!/usr/bin/env python3
"""Step 1 — harvest repository info and a dataset metadata sample from DataCite.

First run : draws a random sample per repository and freezes the DOI list in
            data/sample_dois.csv (the sample is the citable study object).
Later runs: re-fetch exactly those DOIs, so the study is repeatable.
            Use --resample to draw a new random sample.
"""
import argparse, csv, json, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fairgeo.common import RAW, ROOT, USER_AGENT, load_config

SAMPLE_FILE = ROOT / "data" / "sample_dois.csv"


def get(session, url, params=None, tries=4):
    for i in range(tries):
        try:
            r = session.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return None
            print(f"  HTTP {r.status_code}, retry {i + 1}", file=sys.stderr)
        except requests.RequestException as e:
            print(f"  {type(e).__name__}, retry {i + 1}", file=sys.stderr)
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"request failed: {url}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--resample", action="store_true", help="draw a new random sample")
    args = ap.parse_args()
    cfg = load_config()
    api, n = cfg["datacite_api"].rstrip("/"), int(cfg["sample_size_per_repository"])
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    RAW.mkdir(parents=True, exist_ok=True)

    frozen = {}
    if SAMPLE_FILE.exists() and not args.resample:
        with SAMPLE_FILE.open() as f:
            for row in csv.DictReader(f):
                frozen.setdefault(row["client_id"], []).append(row["doi"])
        print(f"Using frozen sample ({sum(map(len, frozen.values()))} DOIs) from {SAMPLE_FILE.name}")

    repos, sample_rows = [], []
    for repo in cfg["repositories"]:
        cid = repo["client_id"]
        client = get(s, f"{api}/clients/{cid}")
        if client is None:
            sys.exit(f"Unknown DataCite client id: {cid}")
        ca = client["data"]["attributes"]
        if cid in frozen:
            records = []
            for doi in frozen[cid]:
                d = get(s, f"{api}/dois/{quote(doi, safe='/')}", {"affiliation": "true"})
                if d:
                    records.append(d["data"])
            total = get(s, f"{api}/dois", {"client-id": cid, "resource-type-id": cfg["resource_type"],
                                           "page[size]": 1})["meta"]["total"]
        else:
            page = get(s, f"{api}/dois", {"client-id": cid, "resource-type-id": cfg["resource_type"],
                                          "random": "true", "page[size]": n, "affiliation": "true"})
            records, total = page["data"][:n], page["meta"]["total"]
        (RAW / f"datacite_{cid}.json").write_text(json.dumps(records, ensure_ascii=False, indent=1))
        repos.append({"client_id": cid, "repository_name": ca.get("name"),
                      "re3data_doi": (ca.get("re3data") or "").replace("https://doi.org/", ""),
                      "repository_url": ca.get("url"), "datasets_at_datacite": total,
                      "sampled": len(records)})
        sample_rows += [{"client_id": cid, "doi": r["attributes"]["doi"]} for r in records]
        print(f"{cid:22s} {ca.get('name', '')[:45]:45s} total={total:>7} sampled={len(records)}")

    with (ROOT / "data" / "repositories.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(repos[0]))
        w.writeheader(); w.writerows(repos)
    with SAMPLE_FILE.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["client_id", "doi"])
        w.writeheader(); w.writerows(sample_rows)
    (ROOT / "data" / "harvest_info.json").write_text(json.dumps({
        "harvested_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "api": api, "sample_size_per_repository": n, "n_records": len(sample_rows)}, indent=1))
    print(f"Done: {len(sample_rows)} records -> data/raw/, DOI list -> data/sample_dois.csv")


if __name__ == "__main__":
    main()
