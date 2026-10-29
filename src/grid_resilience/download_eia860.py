"""Download the official public EIA-860 annual ZIP and extract workbook inputs.

This data acquisition step needs no EIA API key; the key remains required for
hourly EIA-930 API data. Preserve the official archive and source hashes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile
import re

URL = "https://www.eia.gov/electricity/data/eia860/archive/xls/eia8602024.zip"

def obtain(destination, source_url=URL):
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    archive = root / "eia8602024.zip"
    if not archive.exists():
        with urlopen(source_url, timeout=180) as response:
            data = response.read()
        if not data.startswith(b"PK"):
            raise ValueError("EIA download was not a ZIP archive")
        archive.write_bytes(data)
    files = {}
    with ZipFile(archive) as z:
        for typ, marker in (("generators", "3_1_Generator2024"),
                            ("plants", "2___Plant2024")):
            matching = [name for name in z.namelist()
                        if re.sub(r"[^a-z0-9]", "", marker.casefold()) in re.sub(r"[^a-z0-9]", "", Path(name).stem.casefold())
                        and name.lower().endswith((".xlsx", ".xlsm", ".xls"))]
            if len(matching) != 1:
                raise ValueError(f"Expected one {marker} workbook, found {matching}")
            item = matching[0]
            target = root / Path(item).name
            target.write_bytes(z.read(item))
            files[typ] = str(target)
    result = {
        "archive_url": source_url,
        "archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "extraction": files,
        "year": 2024,
        "meaning": "year-end nameplate inventory, not hourly generator availability",
    }
    (root / "download_manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="data/external/eia860_2024")
    a = p.parse_args()
    result = obtain(a.output)
    print("Downloaded/validated EIA-860 2024 archive and two workbooks")
    print(result["archive_sha256"])

if __name__ == "__main__":
    main()
