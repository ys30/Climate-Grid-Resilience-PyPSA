from pathlib import Path
from zipfile import ZipFile
from grid_resilience.download_eia860 import obtain

def test_eia860_download_manifest_from_cached_zip(tmp_path):
    archive = tmp_path / "eia8602024.zip"
    with ZipFile(archive, "w") as z:
        z.writestr("folder/3_1_Generator2024.xlsx", b"generator fixture")
        z.writestr("folder/2___Plant2024.xlsx", b"plant fixture")
    result = obtain(tmp_path)
    assert Path(result["extraction"]["generators"]).read_bytes() == b"generator fixture"
    assert Path(result["extraction"]["plants"]).read_bytes() == b"plant fixture"
    assert len(result["archive_sha256"]) == 64
    assert (tmp_path / "download_manifest.json").exists()
