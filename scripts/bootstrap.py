#!/usr/bin/env python3
from __future__ import annotations
import ast, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "ai-project.yaml"


def parse_scalar(value: str):
    value = value.strip()
    if value.lower() == "true": return True
    if value.lower() == "false": return False
    if value in {"null", "~"}: return None
    if value.startswith(("[", "{", "'", '"')):
        return ast.literal_eval(value)
    if re.fullmatch(r"-?\d+", value): return int(value)
    return value


def load_yaml_subset(path: Path) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, raw in enumerate(lines, 1):
        if not raw.strip() or raw.lstrip().startswith("#") or raw.strip().startswith("- "):
            continue
        if "\t" in raw or ":" not in raw:
            raise SystemExit(f"Unsupported YAML at {path}:{number}")
        indent = len(raw) - len(raw.lstrip(" "))
        while indent <= stack[-1][0]: stack.pop()
        parent = stack[-1][1]
        key, value = raw.strip().split(":", 1)
        if value.strip(): parent[key] = parse_scalar(value)
        else:
            parent[key] = {}
            stack.append((indent, parent[key]))
    return root


def get(data: dict, *keys: str, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current: return default
        current = current[key]
    return current


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def chain(commands: list[str]) -> str:
    return " && ".join(f"({command})" for command in commands)


def generate_env(data: dict) -> str:
    fmt_check: list[str] = []
    fmt_apply: list[str] = []
    lint: list[str] = []
    tests: list[str] = []
    security: list[str] = []
    build: list[str] = []

    if get(data, "stacks", "python", "enabled", default=False):
        fmt_check += ["ruff format --check ."]
        fmt_apply += ["ruff format ."]
        lint += ["ruff check .", "mypy ."]
        tests += ["pytest"]
        security += ["bandit -q -r . -x tests,.venv,venv", "pip-audit"]
        build += ["python -m build"]

    if get(data, "stacks", "react", "enabled", default=False):
        directory = str(get(data, "stacks", "react", "directory", default="frontend"))
        manager = str(get(data, "stacks", "react", "package_manager", default="npm"))
        runner = {"npm": "npm run", "pnpm": "pnpm run", "yarn": "yarn"}.get(manager, f"{manager} run")
        prefix = f"cd {shell_quote(directory)} && "
        fmt_check += [prefix + runner + " format:check"]
        fmt_apply += [prefix + runner + " format"]
        lint += [prefix + runner + " lint", prefix + runner + " typecheck"]
        tests += [prefix + runner + " test"]
        security += [prefix + manager + " audit --audit-level=high"]
        build += [prefix + runner + " build"]

    if get(data, "stacks", "bash", "enabled", default=False):
        lint += ["find . -type f -name '*.sh' -not -path './.git/*' -print0 | xargs -0 -r shellcheck"]
        tests += ["if [ -d tests/shell ]; then bats tests/shell; fi"]

    if get(data, "stacks", "dotnet", "enabled", default=False):
        solution = str(get(data, "stacks", "dotnet", "solution", default="") or ".")
        target = shell_quote(solution)
        fmt_check += [f"dotnet format {target} --verify-no-changes"]
        fmt_apply += [f"dotnet format {target}"]
        lint += [f"dotnet build {target} --no-restore -warnaserror"]
        tests += [f"dotnet test {target} --no-restore"]
        security += [f"dotnet list {target} package --vulnerable --include-transitive"]
        build += [f"dotnet build {target} --no-restore"]
        if get(data, "stacks", "dotnet", "powershell", default=False):
            lint += ['pwsh -NoProfile -Command "Invoke-ScriptAnalyzer -Path . -Recurse -Severity Warning,Error"']
            tests += ['pwsh -NoProfile -Command "if (Test-Path tests/powershell) { Invoke-Pester tests/powershell -CI }"']

    strict = bool(get(data, "quality", "strict", default=True))
    commands = {
        "FORMAT_CHECK_CMD": chain(fmt_check), "FORMAT_APPLY_CMD": chain(fmt_apply),
        "LINT_CMD": chain(lint), "TEST_CMD": chain(tests),
        "SECURITY_CMD": chain(security), "BUILD_CMD": chain(build),
    }
    flags = {
        "REQUIRE_FORMAT_CHECK": strict and get(data, "quality", "require_format", default=True),
        "REQUIRE_LINT": strict and get(data, "quality", "require_lint", default=True),
        "REQUIRE_TEST": strict and get(data, "quality", "require_tests", default=True),
        "REQUIRE_SECURITY": strict and get(data, "quality", "require_security", default=True),
        "REQUIRE_DEPENDENCY_POLICY": get(data, "quality", "require_dependency_policy", default=True),
        "REQUIRE_DEPENDENCY_SCANNERS": strict and get(data, "quality", "require_dependency_scanners", default=True),
        "REQUIRE_BUILD": strict and get(data, "quality", "require_build", default=True),
        "REQUIRE_LOCKFILES": True, "REJECT_FLOATING_VERSIONS": True,
        "DEPENDENCY_ALLOWLIST_MODE": False,
    }
    result = ["# Generated by scripts/bootstrap.py from config/ai-project.yaml.", ""]
    result += [f"{key}={shell_quote(value)}" for key, value in commands.items()]
    result += [f"{key}={1 if value else 0}" for key, value in flags.items()]
    return "\n".join(result) + "\n"


def update_context(data: dict) -> None:
    path = ROOT / "docs/ai/PROJECT_CONTEXT.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Bootstrap configuration"
    name = get(data, "project", "name", default="CHANGE_ME")
    profile = get(data, "project", "profile", default="python")
    mcp = get(data, "engineering_knowledge", "mcp_server", default="engineering-knowledge")
    state = "enabled" if get(data, "engineering_knowledge", "enabled", default=False) else "disabled"
    block = f"\n{marker}\n\n- Project name: `{name}`\n- Primary profile: `{profile}`\n- Engineering knowledge MCP: `{mcp}` ({state})\n- Configuration source: `config/ai-project.yaml`\n"
    text = text.split(marker)[0].rstrip() + block if marker in text else text.rstrip() + "\n" + block
    path.write_text(text, encoding="utf-8")


def create_idea(data: dict) -> None:
    if not get(data, "ide", "create_git_mapping", default=True): return
    idea = ROOT / ".idea"
    idea.mkdir(exist_ok=True)
    (idea / "vcs.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<project version="4">\n  <component name="VcsDirectoryMappings">\n    <mapping directory="$PROJECT_DIR$" vcs="Git" />\n  </component>\n</project>\n', encoding="utf-8")


def main() -> None:
    data = load_yaml_subset(CONFIG)
    (ROOT / "scripts/project.env").write_text(generate_env(data), encoding="utf-8")
    update_context(data)
    create_idea(data)
    for path in (ROOT / "scripts").glob("*.sh"):
        path.chmod(path.stat().st_mode | 0o111)
    print("[bootstrap] Generated scripts/project.env")
    print("[bootstrap] Updated docs/ai/PROJECT_CONTEXT.md")
    print("[bootstrap] Created .idea/vcs.xml when enabled")
    print("[bootstrap] AI rules are ready under .aiassistant/rules/")
    review = get(data, "ide", "self_review_rules", default=".aiassistant/review/self-review.md")
    print("[bootstrap] One manual IntelliJ setting remains:")
    print("  Settings > Tools > AI Assistant > Project Settings")
    print(f'  Path to rules for AI Self-Review: $PROJECT_DIR$/{review}')
    print("[bootstrap] Install the required tools, then run ./scripts/verify.sh")


if __name__ == "__main__":
    main()
