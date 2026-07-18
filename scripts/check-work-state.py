#!/usr/bin/env python3
"""Validate temporary agent work artifacts without modifying them."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "docs" / "ai" / "CURRENT_PLAN.md"
WORK_ROOT = ROOT / "docs" / "ai" / "work"
VALID_STATUSES = {
    "draft",
    "ready",
    "in-progress",
    "blocked",
    "implemented",
    "verified",
    "reviewed",
    "done",
}


def extract_field(text: str, field: str) -> str | None:
    match = re.search(rf"^-\s*{re.escape(field)}:\s*(.+?)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip().strip("`")


def main() -> int:
    if not CURRENT.exists():
        print("FAIL: docs/ai/CURRENT_PLAN.md is missing.")
        return 1

    current_text = CURRENT.read_text(encoding="utf-8")
    if "No active requirement." in current_text:
        print("PASS: no active temporary work declared.")
        return 0

    errors: list[str] = []
    work_dir_value = extract_field(current_text, "Work directory")
    spec_value = extract_field(current_text, "Specification")
    plan_value = extract_field(current_text, "Plan")

    if not work_dir_value:
        errors.append("CURRENT_PLAN.md must contain a 'Work directory' field.")
        work_dir = None
    else:
        work_dir = ROOT / work_dir_value.rstrip("/")
        try:
            work_dir.relative_to(WORK_ROOT)
        except ValueError:
            errors.append("Work directory must be below docs/ai/work/.")
        if not work_dir.is_dir():
            errors.append(f"Declared work directory does not exist: {work_dir_value}")


    if spec_value and spec_value.lower() != "not-required":
        spec = ROOT / spec_value
        if not spec.is_file():
            errors.append(f"Declared specification does not exist: {spec_value}")
        else:
            spec_text = spec.read_text(encoding="utf-8")
            spec_status = extract_field(spec_text, "Status")
            ready = extract_field(spec_text, "Ready for implementation")
            current_status = extract_field(current_text, "Status")
            implementation_phases = {"planning", "implementation", "verification", "review", "remediation", "closeout"}
            if current_status in implementation_phases:
                if spec_status != "ready-for-implementation":
                    errors.append(f"Specification must be ready-for-implementation during {current_status}; found '{spec_status}'")
                if ready != "yes":
                    errors.append(f"Specification must declare 'Ready for implementation: yes' during {current_status}")

    if not plan_value:
        errors.append("CURRENT_PLAN.md must contain a 'Plan' field.")
    else:
        plan = ROOT / plan_value
        if not plan.is_file():
            errors.append(f"Declared plan does not exist: {plan_value}")

    task_files = sorted(work_dir.glob("tasks/*.md")) if work_dir and work_dir.is_dir() else []
    for task_file in task_files:
        text = task_file.read_text(encoding="utf-8")
        status = extract_field(text, "Status")
        if status is None:
            errors.append(f"{task_file.relative_to(ROOT)}: missing Status field")
        elif status not in VALID_STATUSES:
            errors.append(
                f"{task_file.relative_to(ROOT)}: invalid status '{status}'; "
                f"expected one of {', '.join(sorted(VALID_STATUSES))}"
            )

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    print(f"PASS: active work state is structurally valid; {len(task_files)} task file(s) checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
