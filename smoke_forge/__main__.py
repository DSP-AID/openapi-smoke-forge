"""CLI: python -m smoke_forge <spec-path-or-url> [--base-url URL] [-o OUTDIR]

Generates test_generated_smoke.py next to the spec (or in -o dir).
If --base-url is omitted, it is taken from the spec's servers[0].url.
"""

from __future__ import annotations

import argparse
import sys

from .forge import generate_tests, load_spec, write_suite


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="smoke_forge", description="OpenAPI 3.x -> pytest smoke suite")
    ap.add_argument("spec", help="path or http(s) URL of an OpenAPI 3.x JSON spec")
    ap.add_argument("--base-url", default=None, help="API base URL (default: spec servers[0].url)")
    ap.add_argument("-o", "--outdir", default=".", help="output directory (default: .)")
    args = ap.parse_args(argv)

    spec = load_spec(args.spec)
    base = args.base_url or (spec.get("servers") or [{}])[0].get("url")
    if not base:
        print("error: no --base-url and no servers[0].url in spec", file=sys.stderr)
        return 2
    source = generate_tests(spec, base)
    target = write_suite(args.outdir, source)
    n = source.splitlines()[0]
    print(f"wrote {target} ({n.strip('# ')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
