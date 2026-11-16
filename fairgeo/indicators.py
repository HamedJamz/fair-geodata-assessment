"""Transparent, metadata-level FAIR indicators computed from a DataCite record.

Each indicator is a yes/no test on the DataCite JSON of one dataset. They are
*inspired by* the FAIRsFAIR data object assessment metrics but are NOT the
official F-UJI metrics: they only look at what the repository registered at
DataCite, not at the landing page or the data files themselves.
"""
from __future__ import annotations

OPEN_LICENSE_PREFIXES = ("cc0", "cc-by-1", "cc-by-2", "cc-by-3", "cc-by-4",
                         "cc-by-sa", "pddl", "odc-by", "odbl")
OPEN_LICENSE_URL_PARTS = ("creativecommons.org/licenses/by/",
                          "creativecommons.org/licenses/by-sa/",
                          "creativecommons.org/publicdomain/zero")
PROVENANCE_RELATIONS = {"IsDerivedFrom", "IsDocumentedBy", "IsDescribedBy",
                        "IsSupplementTo", "IsSourceOf", "IsCompiledBy"}

# id -> (FAIR principle letter, short label, what is tested)
INDICATORS = {
    "F1_doi_findable":      ("F", "DOI registered & findable", "DOI state is 'findable'"),
    "F2_description":       ("F", "Description >= 100 chars", "at least one description of 100+ characters"),
    "F2_keywords":          ("F", "Keywords", "at least one subject/keyword"),
    "F2_creator_pid":       ("F", "Creator PID (ORCID)", "at least one creator has a persistent identifier"),
    "F2_spatial_coverage":  ("F", "Spatial coverage", "at least one geoLocation"),
    "F2_temporal_coverage": ("F", "Temporal coverage", "a date of type Collected or Coverage"),
    "A1_landing_page":      ("A", "Landing page URL (https)", "registered URL uses https"),
    "A1_size_declared":     ("A", "Size declared", "at least one size statement"),
    "I1_format_declared":   ("I", "File format declared", "at least one format"),
    "I2_controlled_vocab":  ("I", "Keywords from vocabulary", "a subject with scheme or URI"),
    "I3_related_ids":       ("I", "Linked to other objects", "at least one relatedIdentifier"),
    "I3_affiliation_pid":   ("I", "Affiliation PID (ROR)", "a creator affiliation with identifier"),
    "R1_license":           ("R", "License stated", "rightsList not empty"),
    "R1_license_machine":   ("R", "License machine-readable", "rights with URI or SPDX identifier"),
    "R1_license_open":      ("R", "Open license (CC0/BY/BY-SA)", "license is CC0, CC BY, CC BY-SA or ODC equivalent"),
    "R1_provenance":        ("R", "Provenance information", "Methods description or provenance relation"),
    "R1_funding":           ("R", "Funding reference", "at least one fundingReference"),
    "R1_schema_v4":         ("R", "DataCite schema 4.x", "metadata follow DataCite kernel 4"),
}
PRINCIPLES = {"F": "Findable", "A": "Accessible", "I": "Interoperable", "R": "Reusable"}


def _lst(a, key):
    v = a.get(key)
    return v if isinstance(v, list) else []


def _is_open(r: dict) -> bool:
    ident = (r.get("rightsIdentifier") or "").lower()
    uri = (r.get("rightsUri") or "").lower()
    return ident.startswith(OPEN_LICENSE_PREFIXES) or any(p in uri for p in OPEN_LICENSE_URL_PARTS)


def assess(attributes: dict) -> dict:
    """Return {indicator_id: 0|1} for one DataCite `attributes` dict."""
    a = attributes or {}
    creators = _lst(a, "creators")
    subjects = _lst(a, "subjects")
    rights = _lst(a, "rightsList")
    related = _lst(a, "relatedIdentifiers")
    descr = _lst(a, "descriptions")

    def affil_pid(c):
        return any(isinstance(x, dict) and x.get("affiliationIdentifier")
                   for x in (c.get("affiliation") or []))

    res = {
        "F1_doi_findable": a.get("state") == "findable",
        "F2_description": any(len((d.get("description") or "").strip()) >= 100 for d in descr),
        "F2_keywords": any((s.get("subject") or "").strip() for s in subjects),
        "F2_creator_pid": any(any(n.get("nameIdentifier") for n in (c.get("nameIdentifiers") or []))
                              for c in creators),
        "F2_spatial_coverage": len(_lst(a, "geoLocations")) > 0,
        "F2_temporal_coverage": any(d.get("dateType") in ("Collected", "Coverage") and d.get("date")
                                    for d in _lst(a, "dates")),
        "A1_landing_page": str(a.get("url") or "").lower().startswith("https://"),
        "A1_size_declared": len(_lst(a, "sizes")) > 0,
        "I1_format_declared": len(_lst(a, "formats")) > 0,
        "I2_controlled_vocab": any(s.get("subjectScheme") or s.get("valueUri") or s.get("schemeUri")
                                   for s in subjects),
        "I3_related_ids": len(related) > 0,
        "I3_affiliation_pid": any(affil_pid(c) for c in creators),
        "R1_license": len(rights) > 0,
        "R1_license_machine": any(r.get("rightsUri") or r.get("rightsIdentifier") for r in rights),
        "R1_license_open": any(_is_open(r) for r in rights),
        "R1_provenance": any(d.get("descriptionType") == "Methods" for d in descr)
                         or any(r.get("relationType") in PROVENANCE_RELATIONS for r in related),
        "R1_funding": len(_lst(a, "fundingReferences")) > 0,
        "R1_schema_v4": "kernel-4" in str(a.get("schemaVersion") or ""),
    }
    assert set(res) == set(INDICATORS)
    return {k: int(bool(v)) for k, v in res.items()}


def scores(ind: dict) -> dict:
    """Percent score per principle (share of its indicators passed) and overall
    score (share of ALL indicators passed, so every indicator has equal weight)."""
    out = {}
    for letter in PRINCIPLES:
        vals = [ind[k] for k, meta in INDICATORS.items() if meta[0] == letter]
        out[f"score_{letter}"] = round(100 * sum(vals) / len(vals), 1)
    out["score_FAIR"] = round(100 * sum(ind.values()) / len(ind), 1)
    return out
