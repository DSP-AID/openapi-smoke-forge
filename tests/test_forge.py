"""Offline tests for openapi-smoke-forge (no network needed)."""

from __future__ import annotations

import json

import pytest

from smoke_forge.forge import fill_path, generate_tests, load_spec, operations, write_suite

SPEC = {
    "openapi": "3.0.0",
    "servers": [{"url": "https://example.test"}],
    "paths": {
        "/health": {"get": {"responses": {"200": {"description": "ok"}}}},
        "/items/{item_id}": {
            "parameters": [
                {"name": "item_id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "get": {"responses": {"200": {"description": "ok"}}},
            "post": {"responses": {"201": {"description": "created"}}},
        },
        "/report/{fmt}": {
            "get": {
                "parameters": [{"name": "fmt", "in": "path", "schema": {"enum": ["json", "csv"]}}],
                "responses": {"200": {"description": "ok"}},
            }
        },
        "/secret": {"head": {"responses": {"200": {"description": "ok"}}}},
    },
}


def test_operations_covers_only_get_and_head():
    ops = operations(SPEC)
    assert [(m, p) for m, p, _ in ops] == [
        ("get", "/health"),
        ("get", "/items/{item_id}"),
        ("get", "/report/{fmt}"),
        ("head", "/secret"),
    ]


def test_fill_path_uses_examples_and_schema_types():
    item = SPEC["paths"]["/items/{item_id}"]
    assert fill_path("/items/{item_id}", item, item["get"]) == "/items/1"
    rep = SPEC["paths"]["/report/{fmt}"]
    assert fill_path("/report/{fmt}", rep, rep["get"]) == "/report/json"


def test_fill_path_prefers_explicit_example():
    op = {"parameters": [{"name": "rid", "example": "room_0003"}]}
    assert fill_path("/rooms/{rid}", {}, op) == "/rooms/room_0003"


def test_generate_tests_one_function_per_smoke_op():
    src = generate_tests(SPEC, "https://example.test/")
    tree = compile(src, "<gen>", "exec")  # generated source must be valid Python
    assert tree is not None
    for name in (
        "test_get_health",
        "test_get_items_item_id",
        "test_get_report_fmt",
        "test_head_secret",
    ):
        assert f"def {name}():" in src, name
    assert "def test_post" not in src  # POST is not smokeable
    assert 'BASE_URL = "https://example.test"' in src
    assert src.splitlines()[0] == "# 4 smoke tests generated"


def test_generated_smoke_assertion_is_below_500():
    src = generate_tests(SPEC, "https://example.test")
    assert "assert status < 500" in src


def test_load_spec_rejects_non_spec(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"hello": 1}), encoding="utf-8")
    with pytest.raises(TypeError, match="missing 'paths'"):
        load_spec(str(bad))


def test_write_suite_creates_file(tmp_path):
    src = generate_tests(SPEC, "https://example.test")
    target = write_suite(str(tmp_path / "out"), src)
    assert target.exists() and target.read_text(encoding="utf-8") == src
