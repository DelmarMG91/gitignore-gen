# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Nothing yet.

## [0.1.0] - 2025-01-15

### Added

- 15 curated `.gitignore` templates: python, node, go, rust, java, c, cpp, macos,
  windows, linux, vscode, jetbrains, git, docker, and terraform.
- `list` command with one-line template descriptions.
- `show` command with exit code `2` for unknown template names.
- `detect` command that scans project markers and suggests an `add` invocation.
- `add` command with multi-template merging, de-duplication, append-safe writes,
  and `--dry-run` support.
- `init` command that detects project types and writes `.gitignore` automatically.
- Global `--version` and `--help` flags.
- pytest suite covering templates, detection, merging, file writing, and CLI behaviour.

[Unreleased]: https://github.com/DelmarMG91/gitignore-gen/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/DelmarMG91/gitignore-gen/releases/tag/v0.1.0
