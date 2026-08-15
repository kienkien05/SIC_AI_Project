from __future__ import annotations

import argparse
import json

from attendance_ml.data import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a validated identity manifest")
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--scenario", default="normal")
    parser.add_argument("--subject-mode", choices=["folder", "filename"], default="folder")
    parser.add_argument("--val-fraction", type=float, default=0.15)
    parser.add_argument("--test-fraction", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    stats = build_manifest(
        root=args.root,
        output=args.output,
        source=args.source,
        scenario=args.scenario,
        subject_mode=args.subject_mode,
        val_fraction=args.val_fraction,
        test_fraction=args.test_fraction,
        seed=args.seed,
    )
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
