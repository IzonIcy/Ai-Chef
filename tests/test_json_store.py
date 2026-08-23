"""Tests for the shared atomic JSON store."""

import json

from json_store import load_json, save_json_atomic


def test_save_then_load_roundtrips(tmp_path):
    path = tmp_path / "data.json"
    payload = {"a": 1, "list": ["x", "y"]}
    save_json_atomic(path, payload)
    assert load_json(path, None) == payload


def test_load_missing_file_returns_default(tmp_path):
    assert load_json(tmp_path / "nope.json", []) == []
    assert load_json(tmp_path / "nope.json", {"d": 1}) == {"d": 1}


def test_load_corrupt_file_returns_default(tmp_path):
    path = tmp_path / "corrupt.json"
    path.write_text("{not valid json!!")
    assert load_json(path, "fallback") == "fallback"


def test_save_replaces_existing_file_atomically(tmp_path):
    path = tmp_path / "data.json"
    save_json_atomic(path, {"version": 1})
    save_json_atomic(path, {"version": 2})
    assert json.loads(path.read_text()) == {"version": 2}
    # No temp file left behind.
    assert not (tmp_path / "data.json.tmp").exists()


def test_save_creates_parent_directories(tmp_path):
    path = tmp_path / "deep" / "nested" / "dir" / "data.json"
    save_json_atomic(path, [1, 2])
    assert load_json(path, None) == [1, 2]
