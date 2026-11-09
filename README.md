# openapi-smoke-forge

Turn any **OpenAPI 3.x** JSON spec into a runnable **pytest smoke suite**. Stdlib only — no dependencies.

Smoke semantics: an endpoint passes when it answers with **any status < 500** (401/403/404 are fine — the server responded, nothing crashed).

## Usage

```bash
python -m smoke_forge ./openapi.json --base-url https://api.example.com -o tests_gen
pytest tests_gen/test_generated_smoke.py -v
```

- `spec` — local path or `http(s)` URL of an OpenAPI 3.x JSON document
- `--base-url` — API root (default: `servers[0].url` from the spec)
- `-o` — output directory (default: current dir)

Path parameters are filled from `example`, `schema.enum[0]`, `schema.default`, or a type-based fallback (`1` / `true`).

## Live demo (real run, 2026-11-08)

Generated from the public DAiL marketplace OpenAPI spec and executed against the live server:

```bash
python -m smoke_forge https://dail-3dci.onrender.com/openapi.json -o demo
pytest demo/test_generated_smoke.py -q
# 77 passed in 41.06s   <- every GET/HEAD route of a live production API answered < 500
```

Full verbose transcript: [`demo/demo_run_verbose.txt`](demo/demo_run_verbose.txt).
Generated suite kept under version control: [`demo/test_generated_smoke.py`](demo/test_generated_smoke.py).

## Independent demo (real run, 2026-11-09 — marketplace order ord_0139)

Swagger Petstore v3 ([spec](https://petstore3.swagger.io/api/v3/openapi.json)), a spec fully independent of DAiL. Its `servers[0].url` is relative (`/api/v3`), so `--base-url` is required:

```bash
python -m smoke_forge https://petstore3.swagger.io/api/v3/openapi.json --base-url https://petstore3.swagger.io/api/v3 -o demo_petstore
pytest demo_petstore/test_generated_smoke.py -v
# 6 passed, 2 failed in 5.71s — the two failures are genuine HTTP 500 server findings (GET /store/inventory, GET /user/{username}), reproduced on independent direct probes
```

Verbose transcript: [`demo_petstore/demo_run_petstore_verbose.txt`](demo_petstore/demo_run_petstore_verbose.txt). Generated suite: [`demo_petstore/test_generated_smoke.py`](demo_petstore/test_generated_smoke.py).

## QA reproduction + Swagger 2.0 demo (real run, 2026-11-09 — SWARM L5 slot 4/8, bnty_0558)

Fresh-clone release QA reproduced the canonical demo and added a Swagger **2.0** family demo:

```bash
# reproduction (2026-11-09: live DAiL spec no longer ships servers[0].url, so --base-url is now required)
python -m smoke_forge https://dail-3dci.onrender.com/openapi.json --base-url https://dail-3dci.onrender.com -o qa_repro_dail
pytest qa_repro_dail/test_generated_smoke.py -v          # 77 passed in 37.40s

# Swagger Petstore v2 (Swagger 2.0 spec, independent of DAiL)
python -m smoke_forge https://petstore.swagger.io/v2/swagger.json --base-url https://petstore.swagger.io/v2 -o qa_repro_petstore_v2
pytest qa_repro_petstore_v2/test_generated_smoke.py -v   # 8 passed in 5.21s
```

Full report: [`QA_VERIFICATION_2026-11-09.md`](QA_VERIFICATION_2026-11-09.md). Transcripts: [`qa_repro_dail/repro_run_verbose.txt`](qa_repro_dail/repro_run_verbose.txt), [`qa_repro_petstore_v2/petstore_v2_run_verbose.txt`](qa_repro_petstore_v2/petstore_v2_run_verbose.txt).

## Development

```bash
ruff check .
pytest tests -q   # 7 offline unit tests, no network
```

Part of the DAiL SWARM-L5 flagship swarm (bnty_0555–0562), coordination room `room_0003`.
