import argparse
from pathlib import Path

from .io import load_message


def main() -> int:
    parser = argparse.ArgumentParser(description="Conjunction data validator (MVP)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a conjunction message file (JSON/YAML)")
    v.add_argument("path", help="Path to input file")
    v.add_argument("--out", default="out", help="Output directory")

    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    msg = load_message(args.path)

    print(f"Loaded message: {msg.message_id}")
    print(f"TCA: {msg.tca_utc.isoformat()}  Primary: {msg.primary.object_id}  Secondary: {msg.secondary.object_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
