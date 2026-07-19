#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./.ai/tools/create-project.sh [--dry-run] [--force] <target-directory>

Copies reusable project scaffolding without template repository, tests, history,
tooling, temporary work, IDE, environment, cache, or build state. Bootstrap is a
separate, explicit step.

Options:
  --dry-run   Preview without changing the target. Requires rsync.
  --force     Allow overwriting same-named files in a non-empty target.
  -h, --help  Show this help.
USAGE
}

dry_run=0
force=0
args=()
while (($#)); do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --force) force=1 ;;
    -h|--help) usage; exit 0 ;;
    --) shift; args+=("$@"); break ;;
    -*) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *) args+=("$1") ;;
  esac
  shift
done
if ((${#args[@]} != 1)); then
  usage >&2
  exit 2
fi

source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exclude_manifest="${source_dir}/.ai/config/copy-exclude.txt"
if command -v python3 >/dev/null 2>&1; then
  target_dir="$(python3 -c 'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())' "${args[0]}")"
elif command -v python >/dev/null 2>&1; then
  target_dir="$(python -c 'import pathlib, sys; print(pathlib.Path(sys.argv[1]).resolve())' "${args[0]}")"
else
  printf 'Python 3 is required to resolve the target path safely.\n' >&2
  exit 2
fi

if [[ "$source_dir" == "$target_dir" || "$target_dir" == "$source_dir"/* ]]; then
  printf 'Target must be different from and outside the template source directory.\n' >&2
  exit 2
fi
if [[ -d "$target_dir" && -n "$(find "$target_dir" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" && $force -ne 1 ]]; then
  printf 'Target directory is not empty: %s\nUse --force only for an intentional merge.\n' "$target_dir" >&2
  exit 2
fi
if ((dry_run == 0)); then
  mkdir -p "$target_dir"
fi

read_manifest_section() {
  local section="$1"
  local active=0
  local line trimmed
  while IFS= read -r line || [[ -n "${line}" ]]; do
    trimmed="${line#"${line%%[![:space:]]*}"}"
    trimmed="${trimmed%"${trimmed##*[![:space:]]}"}"
    [[ -z "${trimmed}" || "${trimmed}" == \#* ]] && continue
    if [[ "${trimmed}" == \[*] ]]; then
      [[ "${trimmed}" == "[${section}]" ]] && active=1 || active=0
      continue
    fi
    ((active)) && printf '%s\n' "${trimmed}"
  done < "${exclude_manifest}"
}

if [[ ! -f "${exclude_manifest}" ]]; then
  printf 'Copy exclude manifest is missing: %s\n' "${exclude_manifest}" >&2
  exit 2
fi
mapfile -t excluded_paths < <(read_manifest_section relative_paths)
mapfile -t root_directories < <(read_manifest_section root_directories)
mapfile -t state_names < <(read_manifest_section state_names)
mapfile -t state_file_extensions < <(read_manifest_section state_file_extensions)

printf '[create-project] Source: %s\n[create-project] Target: %s\n' "$source_dir" "$target_dir"
if command -v rsync >/dev/null 2>&1; then
  command=(rsync -a --itemize-changes)
  ((dry_run)) && command+=(--dry-run)
  for path in "${excluded_paths[@]}"; do
    command+=(--exclude="/$path")
  done
  for path in "${root_directories[@]}"; do
    command+=(--exclude="/$path/")
  done
  for name in "${state_names[@]}"; do
    command+=(--exclude="$name/")
  done
  for extension in "${state_file_extensions[@]}"; do
    command+=(--exclude="*${extension}")
  done
  command+=("$source_dir/" "$target_dir/")
  "${command[@]}"
else
  if ((dry_run)); then
    printf 'rsync is required for --dry-run.\n' >&2
    exit 2
  fi
  tar_excludes=()
  for path in "${excluded_paths[@]}"; do
    tar_excludes+=("--exclude=./$path")
  done
  for path in "${root_directories[@]}"; do
    tar_excludes+=("--exclude=./$path")
  done
  for name in "${state_names[@]}"; do
    tar_excludes+=(
      "--exclude=./$name" "--exclude=./$name/*"
      "--exclude=*/$name" "--exclude=*/$name/*"
    )
  done
  for extension in "${state_file_extensions[@]}"; do
    tar_excludes+=("--exclude=*${extension}")
  done
  (cd "$source_dir" && tar "${tar_excludes[@]}" -cf - .) | (cd "$target_dir" && tar -xf -)
fi

if ((dry_run)); then
  printf '[create-project] Dry run complete; the target was not changed.\n'
else
  printf '# Current work\n\nNo active requirement.\n' > "${target_dir}/.ai/CURRENT_PLAN.md"
  printf '[create-project] Template copied successfully.\n'
  printf '[create-project] Next: edit .ai/project.yaml and run ./.ai/tools/bootstrap.sh\n'
fi
