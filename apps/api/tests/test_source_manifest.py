import json
from pathlib import Path

MANIFEST = (
    Path(__file__).resolve().parents[3]
    / "workers"
    / "ingestion"
    / "source_manifest.json"
)


def test_source_manifest_is_traceable_and_has_no_unresolved_endpoints():
    sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
    assert len({source["slug"] for source in sources}) == len(sources)

    for source in sources:
        assert source["authority"]
        assert source["version"]
        assert source["official_page"].startswith("https://")
        assert source["limitation"]
        assert "license" in source
        if source["status"].startswith("requires_"):
            assert source["download_endpoint"] is None
