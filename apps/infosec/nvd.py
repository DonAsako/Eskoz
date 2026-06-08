"""Enrich CVE records from the NVD (National Vulnerability Database) API 2.0.

Pure stdlib HTTP, so no extra dependency. No API key is required for low-volume
use (public limit ~5 requests / 30 s); set ``NVD_API_KEY`` in the environment to
raise it. Used by the "Fetch from NVD" admin action on the CVE changelist.
"""

import datetime
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
_TIMEOUT = 15


class NVDError(Exception):
    """Fetching or parsing a CVE from NVD failed."""


def _fetch(cve_id):
    headers = {"User-Agent": "Eskoz/CVE-enrichment"}
    api_key = os.getenv("NVD_API_KEY")
    if api_key:
        headers["apiKey"] = api_key
    req = Request(f"{NVD_URL}?cveId={quote(cve_id)}", headers=headers)  # noqa: S310
    try:
        with urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            payload = json.load(resp)
    except HTTPError as e:
        raise NVDError(f"HTTP {e.code}") from e
    except (URLError, TimeoutError) as e:
        raise NVDError(f"network error: {e.reason if hasattr(e, 'reason') else e}") from e
    except json.JSONDecodeError as e:
        raise NVDError("invalid response") from e
    vulns = payload.get("vulnerabilities") or []
    if not vulns:
        raise NVDError("not found")
    return vulns[0]["cve"]


def _english_description(cve):
    for d in cve.get("descriptions", []):
        if d.get("lang") == "en":
            return d.get("value", "")
    return ""


def _base_score(cve):
    metrics = cve.get("metrics", {})
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if metrics.get(key):
            return metrics[key][0].get("cvssData", {}).get("baseScore")
    return None


def _date(value):
    if not value:
        return None
    try:
        return datetime.date.fromisoformat(value[:10])
    except ValueError:
        return None


def _first_product(cve):
    for conf in cve.get("configurations", []):
        for node in conf.get("nodes", []):
            for match in node.get("cpeMatch", []):
                parts = match.get("criteria", "").split(":")
                if len(parts) > 5 and parts[4]:
                    return f"{parts[3]} {parts[4]}".replace("_", " ")[:200]
    return ""


def _first_reference(cve):
    refs = cve.get("references", [])
    return refs[0]["url"][:300] if refs else ""


def enrich_fields(cve_id):
    """Return a dict of CVE model fields populated from NVD.

    Only non-empty values are returned, so callers never wipe existing data
    with blanks. Raises :class:`NVDError` on any fetch/parse failure.
    """
    cve = _fetch(cve_id)
    fields = {
        "description": _english_description(cve),
        "cvss_score": _base_score(cve),
        "published_date": _date(cve.get("published")),
        "last_modified_date": _date(cve.get("lastModified")),
        "vulnerable_product": _first_product(cve),
        "references_url": _first_reference(cve),
    }
    return {k: v for k, v in fields.items() if v not in ("", None)}
