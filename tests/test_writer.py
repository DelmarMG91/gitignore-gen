"""Tests for template merging and file writing."""

from gitignore_gen import writer
from gitignore_gen.writer import HEADER, merge_lines, render, resolve_names, write_gitignore


def test_merge_deduplicates_rules_preserving_first_order():
    merged = merge_lines(["python", "node"])
    assert merged.count(".env") == 1
    assert merged.count(".DS_Store") == 1
    # Adding macOS later must not duplicate node's existing .DS_Store rule.
    merged_all = merge_lines(["python", "node", "macos", "windows"])
    assert merged_all.count(".DS_Store") == 1
    assert merged_all.index("__pycache__/") < merged_all.index("node_modules/")


def test_resolve_names_accepts_commas_and_case():
    assert resolve_names(["Python, NODE", "go"]) == ["python", "node", "go"]
    assert resolve_names(["python", "python"]) == ["python"]


def test_resolve_unknown_name_raises_keyerror():
    try:
        resolve_names(["python,unknown"])
    except KeyError as exc:
        assert exc.args[0] == "unknown"
    else:  # pragma: no cover
        raise AssertionError("expected KeyError")


def test_write_creates_file_with_header(tmp_path):
    target = tmp_path / ".gitignore"
    result = write_gitignore(target, ["python"])
    assert result.written is True
    assert result.added > 0
    text = target.read_text(encoding="utf-8")
    assert text.startswith(HEADER)
    assert "__pycache__/" in text


def test_write_appends_and_preserves_custom_lines(tmp_path):
    target = tmp_path / ".gitignore"
    target.write_text("my-custom-secret/\n# my comment\n", encoding="utf-8")

    result = write_gitignore(target, ["python"])

    text = target.read_text(encoding="utf-8")
    assert "my-custom-secret/" in text
    assert "# my comment" in text
    assert "__pycache__/" in text
    assert text.count(HEADER) == 1
    assert result.added > 0


def test_write_is_idempotent(tmp_path):
    target = tmp_path / ".gitignore"
    first = write_gitignore(target, ["python", "node"])
    second = write_gitignore(target, ["python", "node"])
    assert first.added > 0
    assert second.added == 0
    assert second.written is True
    assert target.read_text(encoding="utf-8").count("__pycache__/") == 1


def test_dry_run_does_not_write(tmp_path):
    target = tmp_path / ".gitignore"
    result = write_gitignore(target, ["python"], dry_run=True)
    assert result.written is False
    assert result.added > 0
    assert not target.exists()


def test_render_ends_with_single_newline():
    text = render(["go"])
    assert text.startswith(HEADER)
    assert text.endswith("\n")
    assert not text.endswith("\n\n")


def test_template_count_matches_registry():
    assert writer.template_count() == len(writer.list_templates()) == 15
