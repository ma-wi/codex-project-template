#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/lib.sh"

if [[ -f "${REPO_ROOT}/config/dependency-policy.conf" ]]; then
  # shellcheck disable=SC1091
  source "${REPO_ROOT}/config/dependency-policy.conf"
fi

python_cmd="${PYTHON_CMD:-}"
if [[ -z "${python_cmd}" ]]; then
  if has_command python3; then python_cmd=python3
  elif has_command python; then python_cmd=python
  fi
fi
run_or_skip "dependency policy" "${python_cmd:+${python_cmd} scripts/dependency_policy.py}" "${REQUIRE_DEPENDENCY_POLICY:-1}"

scanner_commands=()
if has_command osv-scanner; then
  scanner_commands+=('osv-scanner scan source --recursive .')
fi
if has_command trivy; then
  scanner_commands+=('trivy fs --scanners vuln,secret,misconfig,license --severity UNKNOWN,HIGH,CRITICAL --exit-code 1 .')
fi
if [[ -n "${DEPENDENCY_REPUTATION_CMD:-}" ]]; then
  scanner_commands+=("${DEPENDENCY_REPUTATION_CMD}")
fi
if [[ -n "${DEPENDENCY_SCAN_CMD:-}" ]]; then
  scanner_commands+=("${DEPENDENCY_SCAN_CMD}")
fi

if ((${#scanner_commands[@]} == 0)); then
  run_or_skip "dependency vulnerability/reputation scans" "" "${REQUIRE_DEPENDENCY_SCANNERS:-0}"
else
  joined="$(IFS=' && '; echo "${scanner_commands[*]}")"
  run_command "dependency vulnerability/reputation scans" "${joined}"
fi
