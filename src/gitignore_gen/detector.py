"""Project-type detection based on characteristic files.

The detector inspects a directory (non-recursively at the top level, plus a few
well-known signal directories) and maps observed markers to template names.
Detection is heuristic and side-effect free.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Union


@dataclass(frozen=True)
class Detection:
    """A single template suggestion with the evidence that triggered it.

    Attributes:
        template: Template name that should be added.
        reason: Human readable explanation of the matched marker.
    """

    template: str
    reason: str


#: Ordered list of (template name, predicate, reason) rules.
#: Predicates receive the directory being inspected.
def _any_glob(base: Path, pattern: str) -> bool:
    """Return True if ``base`` contains at least one entry matching ``pattern``."""
    return next(base.glob(pattern), None) is not None


def _detect_python(base: Path) -> Optional[str]:
    if any(base.glob("*.py")):
        return "found Python source files (*.py)"
    if (base / "requirements.txt").is_file():
        return "found requirements.txt"
    if (base / "pyproject.toml").is_file() or (base / "setup.py").is_file():
        return "found Python packaging metadata"
    return None


def _detect_node(base: Path) -> Optional[str]:
    if (base / "package.json").is_file():
        return "found package.json"
    if (base / "yarn.lock").is_file() or (base / "pnpm-lock.yaml").is_file():
        return "found a Node.js lockfile"
    return None


def _detect_go(base: Path) -> Optional[str]:
    if (base / "go.mod").is_file():
        return "found go.mod"
    if (base / "go.sum").is_file():
        return "found go.sum"
    return None


def _detect_rust(base: Path) -> Optional[str]:
    if (base / "Cargo.toml").is_file():
        return "found Cargo.toml"
    if (base / "Cargo.lock").is_file():
        return "found Cargo.lock"
    return None


def _detect_java(base: Path) -> Optional[str]:
    if (base / "pom.xml").is_file():
        return "found pom.xml (Maven)"
    if (base / "build.gradle").is_file():
        return "found build.gradle (Gradle)"
    if (base / "build.gradle.kts").is_file():
        return "found build.gradle.kts (Gradle)"
    return None


def _detect_c_cpp(base: Path) -> List[Detection]:
    found: List[Detection] = []
    if (base / "CMakeLists.txt").is_file():
        found.append(Detection("c", "found CMakeLists.txt (C/C++ project)"))
        found.append(Detection("cpp", "found CMakeLists.txt (C/C++ project)"))
        return found
    if any(base.glob("*.c")) or (base / "Makefile").is_file():
        found.append(Detection("c", "found C sources or Makefile"))
    if any(base.glob("*.cpp")) or any(base.glob("*.cc")) or any(base.glob("*.hpp")):
        found.append(Detection("cpp", "found C++ sources"))
    return found


def _detect_terraform(base: Path) -> Optional[str]:
    if (base / ".terraform").is_dir():
        return "found .terraform directory"
    if any(base.glob("*.tf")):
        return "found Terraform configuration (*.tf)"
    return None


def detect(path: Union[Path, str] = ".") -> List[Detection]:
    """Detect templates that fit the project rooted at ``path``.

    Args:
        path: Directory to inspect. May be a string or :class:`~pathlib.Path`.

    Returns:
        A de-duplicated list of :class:`Detection`, ordered by template
        registration order. Empty when nothing is recognised.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        NotADirectoryError: If ``path`` exists but is not a directory.
    """
    base = Path(path)
    if not base.exists():
        raise FileNotFoundError(f"path does not exist: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"path is not a directory: {base}")

    results: List[Detection] = []

    simple = (
        ("python", _detect_python),
        ("node", _detect_node),
        ("go", _detect_go),
        ("rust", _detect_rust),
        ("java", _detect_java),
    )
    for name, detector in simple:
        reason = detector(base)
        if reason:
            results.append(Detection(name, reason))

    results.extend(_detect_c_cpp(base))

    tf = _detect_terraform(base)
    if tf:
        results.append(Detection("terraform", tf))

    # Keep only the first detection per template to preserve stable ordering.
    seen: set[str] = set()
    unique: List[Detection] = []
    for det in results:
        if det.template in seen:
            continue
        seen.add(det.template)
        unique.append(det)
    return unique


def detected_names(path: Union[Path, str] = ".") -> List[str]:
    """Return just the template names detected at ``path``.

    Args:
        path: Directory to inspect.

    Returns:
        Template names in detection order.
    """
    return [d.template for d in detect(path)]


def _unique(items: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out
