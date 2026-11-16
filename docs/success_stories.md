# Two FAIR success stories from the sample

Selection rule: the record with the highest share of indicators passed in each repository
(`results/success_story_candidates.csv`); the two highest-scoring are described here.
Facts are taken from the public DataCite metadata of the records.

## 1. A mooring dataset that passes every indicator

**Physical oceanography from mooring KPO_1117** — PANGAEA, 2026 —
https://doi.org/10.1594/PANGAEA.995270 — 18 of 18 indicators

Two years of quality-controlled mooring observations from the subpolar North Atlantic
(April 2014 - May 2016, about 7.2 million data points).

What makes it a good example:

- **Findable:** 24 keywords, most of them typed measurement parameters; a geographic
  bounding box; the measurement period as a machine-readable date range; creators with
  persistent identifiers.
- **Interoperable:** declared file format, parameter keywords from a managed vocabulary,
  links to the two cruise reports and to the source data package it was derived from.
- **Reusable:** CC BY 4.0 with licence URI; two funders with Crossref Funder IDs *and*
  grant numbers; instrument-level technical information in the description.

The lesson: none of this needed extra effort from a reader — the repository's curated
submission workflow turns information the authors have anyway into structured metadata.

## 2. A living data product that is cited like a paper

**Geomagnetic Kp index** — GFZ Data Services, 2021 —
https://doi.org/10.5880/Kp.0001 — 16 of 18 indicators, 91 citations registered at DataCite

The IAGA-endorsed Kp index of geomagnetic activity and its derived indices, with data
reaching back to 1932 and regular updates.

What makes it a good example:

- **One stable DOI for a continuously updated product:** the record carries the start of the
  data series (1932) as "Collected" date and an "Updated" date from the week of the harvest.
- **Provenance and credit:** linked to its describing journal article
  (https://doi.org/10.1029/2020SW002641) and to the historical definition of the index;
  the contributing observatories are listed as locations; the funder is given with an identifier.
- **Clear reuse conditions:** CC BY 4.0, machine-readable.
- **Impact is visible:** 91 citations show that a well-described dataset is cited in its own right.

What is still missing in the DataCite record: file format and size — a reminder that even
exemplary records have small, cheap-to-fix gaps.

## The contrast inside the same repository

The Kp index and the GEOFON event records (23 % of indicators passed on average) live in the
same repository. FAIRness is decided at the level of the collection and its curation
workflow, not of the repository name.
