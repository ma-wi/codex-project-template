#!/usr/bin/env bash
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ -f "${SCRIPT_DIR}/project.env" ]]; then
  # shellcheck disable=SC1091
  source "${SCRIPT_DIR}/project.env"
fi

log() {
  printf '[agent-template] %s\n' "$*"
}

fail() {
  printf '[agent-template] ERROR: %s\n' "$*" >&2
  return 1
}

has_command() {
  command -v "$1" >/dev/null 2>&1
}

run_command() {
  local label="$1"
  local command_text="$2"

  log "${label}: ${command_text}"
  (
    cd "${REPO_ROOT}"
    bash -lc "${command_text}"
  )
}

run_or_skip() {
  local label="$1"
  local command_text="$2"
  local required="${3:-0}"

  if [[ -z "${command_text}" ]]; then
    if [[ "${required}" == "1" ]]; then
      fail "${label} is required but no command is configured or detected."
      return 1
    fi
    log "${label}: SKIPPED - no command configured or detected."
    return 0
  fi

  run_command "${label}" "${command_text}"
}

node_runner() {
  if [[ -f "${REPO_ROOT}/pnpm-lock.yaml" ]] && has_command pnpm; then
    printf 'pnpm'
  elif [[ -f "${REPO_ROOT}/yarn.lock" ]] && has_command yarn; then
    printf 'yarn'
  elif has_command npm; then
    printf 'npm'
  else
    printf ''
  fi
}

package_script_exists() {
  local script_name="$1"
  [[ -f "${REPO_ROOT}/package.json" ]] || return 1
  has_command node || return 1
  node -e "const p=require(process.argv[1]); process.exit(p.scripts && p.scripts[process.argv[2]] ? 0 : 1)" \
    "${REPO_ROOT}/package.json" "${script_name}" >/dev/null 2>&1
}

node_script_command() {
  local script_name="$1"
  local runner
  runner="$(node_runner)"
  [[ -n "${runner}" ]] || return 1

  case "${runner}" in
    npm) printf 'npm run %q' "${script_name}" ;;
    pnpm) printf 'pnpm run %q' "${script_name}" ;;
    yarn) printf 'yarn %q' "${script_name}" ;;
  esac
}

detect_format_check() {
  if [[ -x "${REPO_ROOT}/gradlew" ]]; then
    if grep -RqsE 'spotless|ktlint|format' "${REPO_ROOT}"/build.gradle* "${REPO_ROOT}"/settings.gradle* 2>/dev/null; then
      printf './gradlew spotlessCheck'
      return
    fi
  fi
  if package_script_exists format:check; then node_script_command format:check; return; fi
  if package_script_exists prettier:check; then node_script_command prettier:check; return; fi
  if [[ -f "${REPO_ROOT}/pyproject.toml" ]] && has_command ruff; then printf 'ruff format --check .'; return; fi
  if [[ -f "${REPO_ROOT}/go.mod" ]] && has_command gofmt; then printf 'test -z "$(gofmt -l .)"'; return; fi
  if [[ -f "${REPO_ROOT}/Cargo.toml" ]] && has_command cargo; then printf 'cargo fmt --all -- --check'; return; fi
  printf ''
}

detect_format_apply() {
  if [[ -x "${REPO_ROOT}/gradlew" ]]; then
    if grep -RqsE 'spotless|ktlint|format' "${REPO_ROOT}"/build.gradle* "${REPO_ROOT}"/settings.gradle* 2>/dev/null; then
      printf './gradlew spotlessApply'
      return
    fi
  fi
  if package_script_exists format; then node_script_command format; return; fi
  if [[ -f "${REPO_ROOT}/pyproject.toml" ]] && has_command ruff; then printf 'ruff format .'; return; fi
  if [[ -f "${REPO_ROOT}/go.mod" ]] && has_command gofmt; then printf 'gofmt -w .'; return; fi
  if [[ -f "${REPO_ROOT}/Cargo.toml" ]] && has_command cargo; then printf 'cargo fmt --all'; return; fi
  printf ''
}

detect_lint() {
  if [[ -x "${REPO_ROOT}/gradlew" ]]; then printf './gradlew check'; return; fi
  if [[ -f "${REPO_ROOT}/mvnw" && -x "${REPO_ROOT}/mvnw" ]]; then printf './mvnw verify -DskipTests'; return; fi
  if [[ -f "${REPO_ROOT}/pom.xml" ]] && has_command mvn; then printf 'mvn verify -DskipTests'; return; fi
  if package_script_exists lint; then node_script_command lint; return; fi
  if [[ -f "${REPO_ROOT}/pyproject.toml" ]] && has_command ruff; then printf 'ruff check .'; return; fi
  if [[ -f "${REPO_ROOT}/go.mod" ]] && has_command go; then printf 'go vet ./...'; return; fi
  if [[ -f "${REPO_ROOT}/Cargo.toml" ]] && has_command cargo; then printf 'cargo clippy --all-targets --all-features -- -D warnings'; return; fi
  printf ''
}

detect_test() {
  if [[ -x "${REPO_ROOT}/gradlew" ]]; then printf './gradlew test'; return; fi
  if [[ -f "${REPO_ROOT}/mvnw" && -x "${REPO_ROOT}/mvnw" ]]; then printf './mvnw test'; return; fi
  if [[ -f "${REPO_ROOT}/pom.xml" ]] && has_command mvn; then printf 'mvn test'; return; fi
  if package_script_exists test; then node_script_command test; return; fi
  if [[ -f "${REPO_ROOT}/pyproject.toml" ]] && has_command pytest; then printf 'pytest'; return; fi
  if [[ -f "${REPO_ROOT}/go.mod" ]] && has_command go; then printf 'go test ./...'; return; fi
  if [[ -f "${REPO_ROOT}/Cargo.toml" ]] && has_command cargo; then printf 'cargo test --all-features'; return; fi
  printf ''
}

detect_security() {
  local commands=()

  if has_command gitleaks; then commands+=('gitleaks detect --source . --no-banner'); fi
  if [[ -f "${REPO_ROOT}/package.json" ]] && has_command npm; then commands+=('npm audit --audit-level=high'); fi
  if [[ -f "${REPO_ROOT}/requirements.txt" ]] && has_command pip-audit; then commands+=('pip-audit -r requirements.txt'); fi
  if [[ -f "${REPO_ROOT}/pyproject.toml" ]] && has_command pip-audit; then commands+=('pip-audit'); fi
  if [[ -f "${REPO_ROOT}/go.mod" ]] && has_command govulncheck; then commands+=('govulncheck ./...'); fi
  if [[ -f "${REPO_ROOT}/Cargo.toml" ]] && has_command cargo-audit; then commands+=('cargo audit'); fi

  if ((${#commands[@]} == 0)); then
    printf ''
  else
    local joined
    joined="$(IFS=' && '; echo "${commands[*]}")"
    printf '%s' "${joined}"
  fi
}

detect_build() {
  if [[ -x "${REPO_ROOT}/gradlew" ]]; then printf './gradlew assemble'; return; fi
  if [[ -f "${REPO_ROOT}/mvnw" && -x "${REPO_ROOT}/mvnw" ]]; then printf './mvnw package -DskipTests'; return; fi
  if [[ -f "${REPO_ROOT}/pom.xml" ]] && has_command mvn; then printf 'mvn package -DskipTests'; return; fi
  if package_script_exists build; then node_script_command build; return; fi
  if [[ -f "${REPO_ROOT}/pyproject.toml" ]] && has_command python; then printf 'python -m build'; return; fi
  if [[ -f "${REPO_ROOT}/go.mod" ]] && has_command go; then printf 'go build ./...'; return; fi
  if [[ -f "${REPO_ROOT}/Cargo.toml" ]] && has_command cargo; then printf 'cargo build --all-features'; return; fi
  printf ''
}
