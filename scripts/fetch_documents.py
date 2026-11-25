"""Download the source URLs in docs/sources.json into data/documents.
Review each source and respect its publisher's terms of use."""
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "docs" / "sources.json"
DEST = ROOT / "data" / "documents"
DEST.mkdir(parents=True, exist_ok=True)

def main():
    items = json.loads(SOURCES.read_text(encoding="utf-8"))
    for item in items:
        name, url = item["filename"], item["url"]
        target = DEST / name
        if target.exists():
            print(f"SKIP existing: {target}")
            continue
        print(f"Downloading {name} ...")
        response = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0 TCS-Forecast-Research/1.0"})
        response.raise_for_status()
        target.write_bytes(response.content)
        print(f"Saved {target} ({len(response.content):,} bytes)")
    print("Done. Verify downloaded documents and add any missing transcript files.")

if __name__ == "__main__":
    main()
