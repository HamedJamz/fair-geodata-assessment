#!/usr/bin/env python3
"""Step 2 — apply the metadata-level FAIR indicators and build the master table
(one row per dataset, one column per indicator)."""
import json, sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fairgeo.common import RAW, RESULTS, ROOT
from fairgeo.indicators import assess, scores


def first_title(a):
    t = a.get("titles") or []
    return (t[0].get("title") or "").strip() if t else ""


def licenses(a):
    return "; ".join(sorted({(r.get("rightsIdentifier") or r.get("rights") or "").strip()
                             for r in (a.get("rightsList") or [])} - {""}))


def main():
    repos = pd.read_csv(ROOT / "data" / "repositories.csv").set_index("client_id")
    rows = []
    for cid in repos.index:
        for rec in json.loads((RAW / f"datacite_{cid}.json").read_text()):
            a = rec["attributes"]
            ind = assess(a)
            rows.append({"doi": a["doi"], "repository": repos.loc[cid, "repository_name"],
                         "client_id": cid, "title": first_title(a),
                         "publication_year": a.get("publicationYear"),
                         "license": licenses(a), "citation_count": a.get("citationCount"),
                         "landing_page": a.get("url"), **ind, **scores(ind)})
    df = pd.DataFrame(rows)
    RESULTS.mkdir(exist_ok=True)
    df.to_csv(RESULTS / "fair_assessment_table.csv", index=False)
    print(f"{len(df)} datasets x {df.shape[1]} columns -> results/fair_assessment_table.csv")


if __name__ == "__main__":
    main()
