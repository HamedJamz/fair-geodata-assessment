# Data Management Plan — FAIR geodata assessment pilot

| | |
|---|---|
| Project | How FAIR is the metadata of geoscience datasets in German repositories? |
| Responsible | Hamed Jamalzehi, M.Sc. student Geodesy and Geoinformation Science, TU Berlin |
| Period | November 2026 (pilot) |
| Version | 1.0 |

## 1. Data collected and created

| Data | Source / method | Format | Volume |
|---|---|---|---|
| Repository information | DataCite REST API `/clients` (incl. re3data ID) | CSV | < 10 kB |
| Dataset metadata sample (300 records) | DataCite REST API `/dois`, random sample of 50 per repository | JSON | a few MB |
| Frozen sample (DOI list) | written at first harvest | CSV | < 20 kB |
| Assessment table, summaries | computed by the workflow | CSV | < 1 MB |
| Figures | computed by the workflow | PNG | < 1 MB |

No personal or sensitive data are collected. Creator names contained in public DataCite
records are stored only inside the raw metadata and are not analysed.

## 2. Documentation and metadata

- `README.md` describes purpose, workflow, indicators and limitations.
- Every indicator is defined once, in code and in words, in `fairgeo/indicators.py`.
- `data/harvest_info.json` records harvest time, API and sample size (provenance).
- `config.yaml` holds the complete study design; nothing is hard-coded in the scripts.
- Column names in all tables are self-describing; CSV is UTF-8, comma-separated.
- Project-level metadata: `CITATION.cff` and `.zenodo.json` (DataCite-compatible).

## 3. Storage and backup during the project

Working copy on the author's laptop, version-controlled with Git and pushed to GitHub
after each work session. Raw data can be regenerated at any time from the frozen DOI list.

## 4. Legal and ethical aspects

DataCite metadata are published under CC0 and may be reused and redistributed. The code is
released under the MIT licence; tables, figures and texts under CC BY 4.0. Results describe
*metadata records*, not the scientific quality of datasets or the work of individuals;
the limitations are stated wherever results are shown.

## 5. Sharing and long-term preservation

| FAIR principle | How this project meets it |
|---|---|
| Findable | Release archived on Zenodo with a DOI; rich metadata and keywords; public GitHub repository |
| Accessible | Open access via HTTPS, no registration; metadata stay available via DataCite even if files were withdrawn |
| Interoperable | Open, non-proprietary formats (CSV, JSON, PNG, Markdown); identifiers (DOI, re3data, DataCite client ID) kept in all tables |
| Reusable | Explicit licences; documented method and limitations; frozen sample, pinned requirements and unit tests make the study repeatable |

Zenodo guarantees retention for the lifetime of the repository (at least 20 years).

## 6. Responsibilities and resources

The author is responsible for data management. No costs: only open tools and free
infrastructure (Python, GitHub, Zenodo, DataCite API) are used.
