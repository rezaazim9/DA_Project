"""Download only missing source files and verify all pinned checksums."""
from pathlib import Path
from .data_io import verify_sources

if __name__ == "__main__":
    files = verify_sources(Path(__file__).resolve().parents[1], download=True)
    print(f"Verified {len(files)} official source files.")
