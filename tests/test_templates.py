"""Tests for the built-in template registry."""

from gitignore_gen.templates import TEMPLATES, get_template, template_names


EXPECTED = {
    "python",
    "node",
    "go",
    "rust",
    "java",
    "c",
    "cpp",
    "macos",
    "windows",
    "linux",
    "vscode",
    "jetbrains",
    "git",
    "docker",
    "terraform",
}


def test_all_expected_templates_present():
    assert set(template_names()) == EXPECTED
    assert len(TEMPLATES) == len(EXPECTED)


def test_templates_are_non_empty_and_reasonably_sized():
    for name, template in TEMPLATES.items():
        assert name == template.name
        assert template.description.strip(), f"{name} has no description"
        assert 15 <= len(template.lines) <= 40, f"{name} has {len(template.lines)} lines"
        rendered = template.render()
        assert rendered.endswith("\n")
        assert len(rendered.strip().splitlines()) >= 15
        assert "TODO" not in rendered


def test_templates_contain_comments_and_globs():
    for name, template in TEMPLATES.items():
        text = "\n".join(template.lines)
        assert "#" in text, f"{name} should contain comments"
        assert any(ch in text for ch in "*?["), f"{name} should contain glob patterns"


def test_get_template_is_case_insensitive():
    assert get_template("Python") is TEMPLATES["python"]
    assert get_template(" NODE ") is TEMPLATES["node"]


def test_unknown_template_raises_keyerror():
    try:
        get_template("brainfuck")
    except KeyError as exc:
        assert exc.args[0] == "brainfuck"
    else:  # pragma: no cover
        raise AssertionError("expected KeyError")
