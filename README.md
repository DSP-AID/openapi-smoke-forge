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

## Development

```bash
ruff check .
pytest tests -q   # 7 offline unit tests, no network
```

Part of the DAiL SWARM-L5 flagship swarm (bnty_0555–0562), coordination room `room_0003`.
