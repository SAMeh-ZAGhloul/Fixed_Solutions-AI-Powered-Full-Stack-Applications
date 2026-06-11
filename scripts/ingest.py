import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """Parse ingestion CLI arguments."""
    parser = argparse.ArgumentParser(description="Batch ingest documents.")
    parser.add_argument("--dir", default="data/uploads/", help="Directory containing documents")
    return parser.parse_args()


def main() -> None:
    """Phase 2 placeholder for batch ingestion."""
    args = parse_args()
    upload_dir = Path(args.dir)
    files = [path for path in upload_dir.glob("*") if path.suffix.lower() in {".pdf", ".txt", ".md"}]
    print(f"Found {len(files)} ingestable files. Ingestion implementation lands in Phase 2.")


if __name__ == "__main__":
    main()
