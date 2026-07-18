#!/usr/bin/env bash
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures=0

run_gate() {
  local name="$1"
  shift
  printf '\n=== %s ===\n' "${name}"
  if "$@"; then
    printf '=== %s: PASS ===\n' "${name}"
  else
    printf '=== %s: FAIL ===\n' "${name}" >&2
    failures=$((failures + 1))
  fi
}

run_gate "work-state" "${SCRIPT_DIR}/check-work-state.py"
run_gate "documentation" "${SCRIPT_DIR}/check-docs.py"
run_gate "format" "${SCRIPT_DIR}/format.sh" --check
run_gate "lint" "${SCRIPT_DIR}/lint.sh"
run_gate "tests" "${SCRIPT_DIR}/test.sh"
run_gate "dependency policy" "${SCRIPT_DIR}/check-dependencies.sh"
run_gate "security" "${SCRIPT_DIR}/security.sh"
run_gate "build" "${SCRIPT_DIR}/build.sh"

printf '\n'
if ((failures > 0)); then
  printf 'Verification failed: %d gate(s) failed.\n' "${failures}" >&2
  exit 1
fi

printf 'Verification completed without gate failures. Review output for SKIPPED gates; mandatory skipped gates are incomplete.\n'
