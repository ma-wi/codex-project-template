#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

printf '%s\n' '=== template documentation ==='
"${SCRIPT_DIR}/check-docs.py"

printf '%s\n' '=== template shell syntax ==='
while IFS= read -r -d '' script; do
  bash -n "${script}"
done < <(find "${SCRIPT_DIR}" -maxdepth 1 -type f -name '*.sh' -print0)
if ! command -v shellcheck >/dev/null 2>&1; then
  printf '%s\n' 'ERROR: shellcheck is required to verify the template scripts.' >&2
  exit 1
fi
shellcheck "${SCRIPT_DIR}"/*.sh

printf '%s\n' '=== template Python syntax ==='
python3 -c 'import ast, pathlib, sys; [ast.parse(p.read_text(encoding="utf-8"), filename=str(p)) for p in pathlib.Path(sys.argv[1]).rglob("*.py") if not any(x in p.parts for x in (".git", ".venv"))]' "${REPO_ROOT}"

if ! command -v uv >/dev/null 2>&1; then
  printf '%s\n' 'ERROR: pinned uv is required for template quality checks.' >&2
  exit 1
fi
printf '%s\n' '=== template Python quality ==='
uvx --from ruff==0.15.22 ruff format --check "${REPO_ROOT}/.ai/tools" "${REPO_ROOT}/tests"
uvx --from ruff==0.15.22 ruff check "${REPO_ROOT}/.ai/tools" "${REPO_ROOT}/tests"
uvx --from mypy==2.3.0 mypy "${REPO_ROOT}/.ai/tools" "${REPO_ROOT}/tests"
uvx --from bandit==1.9.4 bandit -q -r "${REPO_ROOT}/.ai/tools"

printf '%s\n' '=== template tests ==='
python3 -m unittest discover -s "${REPO_ROOT}/tests" -p 'test_*.py' -v

printf '%s\n' 'Template verification completed without gate failures.'
