#!/usr/bin/env python3
"""Dependency manifest policy checks using only the Python standard library."""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"


def env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, "1" if default else "0") == "1"


def entries(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def add(result: list[tuple[str, str | None]], ecosystem: str, name: str, version: str | None = None) -> None:
    name = name.strip()
    if name:
        result.append((f"{ecosystem}:{name}", version.strip() if version else None))


def read_dependencies() -> list[tuple[str, str | None]]:
    found: list[tuple[str, str | None]] = []
    package_json = ROOT / "package.json"
    if package_json.exists():
        data = json.loads(package_json.read_text(encoding="utf-8"))
        for section in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
            for name, version in (data.get(section) or {}).items():
                add(found, "npm", name, str(version))

    for req_name in ("requirements.txt", "requirements-dev.txt"):
        path = ROOT / req_name
        if path.exists():
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or line.startswith(("-r", "--")):
                    continue
                match = re.match(r"([A-Za-z0-9_.-]+)\s*([<>=!~].*)?$", line.split(";")[0].strip())
                if match:
                    add(found, "pypi", match.group(1).lower().replace("_", "-"), match.group(2))

    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists() and sys.version_info >= (3, 11):
        import tomllib
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        project = data.get("project", {})
        for spec in project.get("dependencies", []) or []:
            match = re.match(r"([A-Za-z0-9_.-]+)\s*(.*)$", spec)
            if match:
                add(found, "pypi", match.group(1).lower().replace("_", "-"), match.group(2))

    cargo = ROOT / "Cargo.toml"
    if cargo.exists() and sys.version_info >= (3, 11):
        import tomllib
        data = tomllib.loads(cargo.read_text(encoding="utf-8"))
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            for name, value in (data.get(section) or {}).items():
                version = value if isinstance(value, str) else str(value.get("version", ""))
                add(found, "cargo", name, version)

    gomod = ROOT / "go.mod"
    if gomod.exists():
        in_block = False
        for raw in gomod.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line == "require (": in_block = True; continue
            if in_block and line == ")": in_block = False; continue
            if line.startswith("require "): line = line[len("require "):]
            elif not in_block: continue
            parts = line.split()
            if len(parts) >= 2:
                add(found, "go", parts[0], parts[1])

    pom = ROOT / "pom.xml"
    if pom.exists():
        try:
            tree = ElementTree.parse(pom)
            root = tree.getroot()
            ns = {"m": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}
            prefix = "m:" if ns else ""
            for dep in root.findall(f".//{prefix}dependencies/{prefix}dependency", ns):
                group = dep.findtext(f"{prefix}groupId", namespaces=ns) or ""
                artifact = dep.findtext(f"{prefix}artifactId", namespaces=ns) or ""
                version = dep.findtext(f"{prefix}version", namespaces=ns)
                if group and artifact:
                    add(found, "maven", f"{group}:{artifact}", version)
        except ElementTree.ParseError as exc:
            print(f"ERROR: cannot parse pom.xml: {exc}", file=sys.stderr)

    return sorted(set(found))


def check_lockfiles(errors: list[str]) -> None:
    requirements = [
        ((ROOT / "package.json").exists(), ["package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb"], "Node.js"),
        ((ROOT / "Cargo.toml").exists(), ["Cargo.lock"], "Rust"),
        ((ROOT / "go.mod").exists(), ["go.sum"], "Go"),
    ]
    for active, candidates, label in requirements:
        if active and not any((ROOT / item).exists() for item in candidates):
            errors.append(f"{label}: required lock/integrity file missing ({', '.join(candidates)})")


def floating(version: str | None) -> bool:
    if version is None:
        return False
    value = version.strip().lower()
    return value in {"", "*", "latest", "x"} or value.startswith(("git+", "http://", "https://")) or re.search(r"(^|[.])x($|[.])", value) is not None


def main() -> int:
    deny = entries(CONFIG / "dependency-denylist.txt")
    allow = entries(CONFIG / "dependency-allowlist.txt")
    allow_mode = env_bool("DEPENDENCY_ALLOWLIST_MODE", False)
    require_lockfiles = env_bool("REQUIRE_LOCKFILES", True)
    reject_floating = env_bool("REJECT_FLOATING_VERSIONS", True)
    dependencies = read_dependencies()
    errors: list[str] = []

    for coordinate, version in dependencies:
        if coordinate in deny:
            errors.append(f"denied dependency: {coordinate}")
        if allow_mode and coordinate not in allow:
            errors.append(f"dependency not on allow-list: {coordinate}")
        if reject_floating and floating(version):
            errors.append(f"floating or unpinned version: {coordinate} ({version!r})")

    if require_lockfiles:
        check_lockfiles(errors)

    print(f"Dependency policy inspected {len(dependencies)} direct dependency entries.")
    for coordinate, version in dependencies:
        print(f"  {coordinate}{' ' + version if version else ''}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Dependency policy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
