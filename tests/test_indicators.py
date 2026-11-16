import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fairgeo.indicators import INDICATORS, assess, scores

RICH = {
    "doi": "10.1234/example", "state": "findable", "url": "https://example.org/ds/1",
    "contentUrl": ["https://example.org/ds/1/data.nc"], "sizes": ["12 MB"], "formats": ["application/x-netcdf"],
    "schemaVersion": "http://datacite.org/schema/kernel-4",
    "descriptions": [{"description": "x" * 150, "descriptionType": "Abstract"},
                     {"description": "processing steps", "descriptionType": "Methods"}],
    "subjects": [{"subject": "sea level", "subjectScheme": "GCMD", "valueUri": "https://gcmd.example/1"}],
    "creators": [{"name": "A, B", "nameIdentifiers": [{"nameIdentifier": "https://orcid.org/0000-0000-0000-0000"}],
                  "affiliation": [{"name": "Uni", "affiliationIdentifier": "https://ror.org/00x"}]}],
    "geoLocations": [{"geoLocationPlace": "Baltic Sea"}],
    "dates": [{"date": "2019/2021", "dateType": "Collected"}],
    "relatedIdentifiers": [{"relatedIdentifier": "10.1/x", "relationType": "IsSupplementTo"}],
    "rightsList": [{"rights": "CC BY 4.0", "rightsUri": "https://creativecommons.org/licenses/by/4.0/legalcode",
                    "rightsIdentifier": "cc-by-4.0"}],
    "fundingReferences": [{"funderName": "DFG"}],
}


def test_rich_record_passes_everything():
    ind = assess(RICH)
    assert set(ind) == set(INDICATORS) and all(ind.values())
    assert scores(ind)["score_FAIR"] == 100.0


def test_empty_record_fails_everything():
    ind = assess({})
    assert not any(ind.values()) and scores(ind)["score_FAIR"] == 0.0


def test_non_open_license_and_old_string_affiliation():
    rec = dict(RICH, rightsList=[{"rights": "CC BY-NC 4.0", "rightsIdentifier": "cc-by-nc-4.0"}],
               creators=[{"name": "A", "affiliation": ["Uni"], "nameIdentifiers": []}])
    ind = assess(rec)
    assert ind["R1_license"] == 1 and ind["R1_license_machine"] == 1 and ind["R1_license_open"] == 0
    assert ind["I3_affiliation_pid"] == 0 and ind["F2_creator_pid"] == 0
