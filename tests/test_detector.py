"""Tests for project-type detection."""

import pytest

from gitignore_gen.detector import detect, detected_names


def _touch(directory, name, content=""):
    path = directory / name
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("marker", "expected"),
    [
        ("app.py", "python"),
        ("requirements.txt", "python"),
        ("package.json", "node"),
        ("go.mod", "go"),
        ("Cargo.toml", "rust"),
        ("pom.xml", "java"),
        ("build.gradle", "java"),
    ],
)
def test_single_marker_detection(tmp_path, marker, expected):
    _touch(tmp_path, marker, "{}")
    assert detected_names(tmp_path) == [expected]


def test_cmake_detects_c_and_cpp(tmp_path):
    _touch(tmp_path, "CMakeLists.txt", "project(demo)")
    names = detected_names(tmp_path)
    assert names == ["c", "cpp"]
    reasons = {d.template: d.reason for d in detect(tmp_path)}
    assert "CMakeLists.txt" in reasons["c"]
    assert "CMakeLists.txt" in reasons["cpp"]


def test_terraform_directory_detection(tmp_path):
    (tmp_path / ".terraform").mkdir()
    assert detected_names(tmp_path) == ["terraform"]


def test_multiple_stacks_are_reported_together(tmp_path):
    _touch(tmp_path, "main.py", "print('hi')")
    _touch(tmp_path, "package.json", "{}")
    _touch(tmp_path, "go.mod", "module demo")

    names = detected_names(tmp_path)
    assert names == ["python", "node", "go"]


def test_empty_directory_detects_nothing(tmp_path):
    assert detect(tmp_path) == []
    assert detected_names(tmp_path) == []


def test_missing_path_raises(tmp_path):
    missing = tmp_path / "nope"
    with pytest.raises(FileNotFoundError):
        detect(missing)


def test_file_path_raises_not_a_directory(tmp_path):
    file_path = _touch(tmp_path, "plain.txt", "x")
    with pytest.raises(NotADirectoryError):
        detect(file_path)
