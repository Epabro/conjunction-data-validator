import argparse

def main() -> int:
    parser = argparse.ArgumentParser(description="Conjunction data validator (MVP)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a conjunction message file (JSON/YAML)")
    v.add_argument("path", help="Path to input file")
    v.add_argument("--out", default="out", help="Output directory")

    args = parser.parse_args()

    print(f"[MVP] Would validate: {args.path} -> output dir: {args.out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
