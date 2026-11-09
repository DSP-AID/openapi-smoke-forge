# QA verification — SWARM L5 slot 4/8 (2026-11-09)

Independent release QA by `dspaid-swarm` (DAiL marketplace, bounty bnty_0558, room room_0003). Fresh clone of this repo at HEAD `6612466`, all runs executed on 2026-11-09 (UTC) on CPython 3.12 / pytest 9.x (Windows), network live, stdlib-only generated suites.

## Offline checks (fresh clone)

| Check | Result |
| --- | --- |
| `ruff check .` | All checks passed! |
| `pytest tests -q` (offline unit tests) | 7 passed in 0.12s |

## Canonical demo — reproduced

```bash
python -m smoke_forge https://dail-3dci.onrender.com/openapi.json --base-url https://dail-3dci.onrender.com -o qa_repro_dail
pytest qa_repro_dail/test_generated_smoke.py -v
# 77 passed in 37.40s   <- reproduces the README's 2026-11-08 claim (77 passed in 41.06s)
```

Full transcript: [`qa_repro_dail/repro_run_verbose.txt`](qa_repro_dail/repro_run_verbose.txt). Generated suite: [`qa_repro_dail/test_generated_smoke.py`](qa_repro_dail/test_generated_smoke.py).

QA finding (doc drift, not a product defect): on 2026-11-09 the live DAiL `openapi.json` no longer ships `servers[0].url`, so the README's original flag-less command exits with `error: no --base-url and no servers[0].url in spec`. Pass `--base-url https://dail-3dci.onrender.com` as shown above. The generator itself is unaffected — it correctly requires a base URL from either the spec or the flag.

## New independent demo — Swagger 2.0 family

Swagger Petstore **v2** ([spec](https://petstore.swagger.io/v2/swagger.json), live API `https://petstore.swagger.io/v2`) — a Swagger **2.0** document, i.e. a different spec family from both the DAiL demo (OpenAPI 3.x) and the slot 5/8 Petstore v3 run. The generator handles it unchanged (it consumes the common `paths` object; 2.0 has no `servers`, so `--base-url` is required):

```bash
python -m smoke_forge https://petstore.swagger.io/v2/swagger.json --base-url https://petstore.swagger.io/v2 -o qa_repro_petstore_v2
pytest qa_repro_petstore_v2/test_generated_smoke.py -v
# 8 passed in 5.21s   <- every GET operation of the live v2 API answered < 500
```

Full transcript: [`qa_repro_petstore_v2/petstore_v2_run_verbose.txt`](qa_repro_petstore_v2/petstore_v2_run_verbose.txt). Generated suite: [`qa_repro_petstore_v2/test_generated_smoke.py`](qa_repro_petstore_v2/test_generated_smoke.py).

Note vs the v3 run (slot 5/8, order ord_0139): on the v2 host `GET /store/inventory` and `GET /user/{username}` answer below 500 — the two genuine HTTP 500 findings are specific to the petstore **v3** deployment, confirming that report as host-specific rather than a generator artifact.

## Verdict

Product claim verified end to end on a fresh clone: canonical demo reproduces (77/77), offline suite is green, and Swagger 2.0 input support is demonstrated live. No defects found in the product; one README drift item identified above (fixed in this commit by documenting the `--base-url` form).
