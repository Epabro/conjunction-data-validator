import argparse
from pathlib import Path

from .io import load_message
from .rules import load_rules
from .validation import validate_message, report_to_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Conjunction data validator (MVP)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="Validate a conjunction message file (JSON/YAML)")
    v.add_argument("path", help="Path to input file")
    v.add_argument("--out", default="out", help="Output directory")
    v.add_argument("--rules", default=None, help="Optional rules.yaml path (threshold overrides)")

    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    msg = load_message(args.path)
    rules = load_rules(args.rules) if args.rules else load_rules("rules.yaml") if Path("rules.yaml").exists() else load_rules(None)

    report = validate_message(msg, rules)

    stem = Path(args.path).stem
    json_path = out_dir / f"{stem}_report.json"
    md_path = out_dir / f"{stem}_report.md"

    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(report_to_markdown(report), encoding="utf-8")

    print(f"OK={report.ok}  pass={report.summary['pass']} warn={report.summary['warn']} fail={report.summary['fail']}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")

    return 0 if report.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
