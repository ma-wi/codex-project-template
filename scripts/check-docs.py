#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ai-project.yaml"


def parse_scalar(value: str):
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value in {"null", "~"}:
        return None
    if value.startswith(("[", "{", "'", '"')):
        return ast.literal_eval(value)
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def load_yaml_subset(path: Path) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#") or raw.strip().startswith("- "):
            continue
        if "\t" in raw or ":" not in raw:
            raise ValueError(f"Unsupported YAML at {path}:{number}")
        indent = len(raw) - len(raw.lstrip(" "))
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        key, value = raw.strip().split(":", 1)
        if value.strip():
            parent[key] = parse_scalar(value)
        else:
            parent[key] = {}
            stack.append((indent, parent[key]))
    return root


def get(data: dict, *keys: str, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def meaningful_lines(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def markdown_links(path: Path):
    text = path.read_text(encoding="utf-8")
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
        target = match.group(1).strip().split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        yield target


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    data = load_yaml_subset(CONFIG)
    budgets = get(data, "documentation", "budgets", default={}) or {}

    budget_files = {
        "agents_md_lines": ROOT / "AGENTS.md",
        "project_context_lines": ROOT / "docs/ai/PROJECT_CONTEXT.md",
        "current_plan_lines": ROOT / "docs/ai/CURRENT_PLAN.md",
    }
    for key, path in budget_files.items():
        limit = budgets.get(key)
        if isinstance(limit, int) and path.exists():
            count = meaningful_lines(path)
            if count > limit:
                warnings.append(f"{path.relative_to(ROOT)} has {count} nonblank lines; budget is {limit}")

    next_limit = budgets.get("next_steps_items")
    next_path = ROOT / "docs/ai/NEXT_STEPS.md"
    if isinstance(next_limit, int) and next_path.exists():
        items = sum(1 for line in next_path.read_text(encoding="utf-8").splitlines() if re.match(r"^\s*(?:[-*]|\d+[.)])\s+", line))
        if items > next_limit:
            warnings.append(f"{next_path.relative_to(ROOT)} has {items} list items; budget is {next_limit}")

    work_limit = budgets.get("active_work_item_lines")
    if isinstance(work_limit, int):
        for path in sorted((ROOT / "docs/ai/work").glob("*/tasks/*.md")):
            count = meaningful_lines(path)
            if count > work_limit:
                warnings.append(f"{path.relative_to(ROOT)} has {count} nonblank lines; budget is {work_limit}")

    placeholders = get(data, "documentation", "forbidden_placeholders", default="CHANGE_ME|TODO_TEMPLATE|<PROJECT_NAME>")
    placeholder_re = re.compile(str(placeholders))
    checked_roots = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / "docs", ROOT / "config"]
    for entry in checked_roots:
        paths = [entry] if entry.is_file() else list(entry.rglob("*.md")) + list(entry.rglob("*.yaml"))
        for path in paths:
            if path.name.endswith(".example") or "templates" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if placeholder_re.search(text):
                warnings.append(f"template placeholder remains in {path.relative_to(ROOT)}")

    for path in list(ROOT.rglob("*.md")):
        if any(part in {".git", ".venv", "node_modules"} for part in path.parts):
            continue
        for target in markdown_links(path):
            target_path = (path.parent / target).resolve()
            try:
                target_path.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not target_path.exists():
                errors.append(f"broken local link in {path.relative_to(ROOT)}: {target}")

    current = ROOT / "docs/ai/CURRENT_PLAN.md"
    if current.exists():
        text = current.read_text(encoding="utf-8")
        if "Status: idle" not in text and "- Status: idle" not in text:
            if "Work directory:" not in text or "Plan:" not in text:
                errors.append("CURRENT_PLAN.md is active but lacks Work directory or Plan pointer")

    print("Documentation consistency check")
    for message in warnings:
        print(f"WARN: {message}")
    for message in errors:
        print(f"ERROR: {message}")
    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: no documentation errors; {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
