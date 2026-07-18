#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/create-project.sh [--dry-run] [--force] <target-directory>

Copies this template into a new project directory while excluding local
repository, IDE, environment, cache, and build artifacts.

Options:
  --dry-run  Show what would be copied without changing the target.
  --force    Allow copying into a non-empty target directory.
  -h, --help Show this help.
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

source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
target_dir="${args[0]}"

mkdir -p "$target_dir"
target_dir="$(cd "$target_dir" && pwd)"

if [[ "$source_dir" == "$target_dir" ]]; then
  printf 'Source and target must be different directories.\n' >&2
  exit 2
fi

if [[ -n "$(find "$target_dir" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" && $force -ne 1 ]]; then
  printf 'Target directory is not empty: %s\n' "$target_dir" >&2
  printf 'Use --force only when merging into that directory is intentional.\n' >&2
  exit 2
fi

excludes=(
  '.git/'
  '.idea/'
  'scripts/project.env'
  '.venv/'
  'venv/'
  'node_modules/'
  '__pycache__/'
  '.pytest_cache/'
  '.mypy_cache/'
  '.ruff_cache/'
  'coverage/'
  'build/'
  'dist/'
  'target/'
  '*.pyc'
  '*.pyo'
  '*.zip'
)

printf '[create-project] Source: %s\n' "$source_dir"
printf '[create-project] Target: %s\n' "$target_dir"

if command -v rsync >/dev/null 2>&1; then
  cmd=(rsync -a --itemize-changes)
  ((dry_run)) && cmd+=(--dry-run)
  for pattern in "${excludes[@]}"; do
    cmd+=(--exclude="$pattern")
  done
  cmd+=("$source_dir/" "$target_dir/")
  "${cmd[@]}"
else
  if ((dry_run)); then
    printf 'rsync is required for --dry-run. Install rsync or run without --dry-run.\n' >&2
    exit 2
  fi

  # Portable fallback. Hidden files such as .gitignore, .github, .aiassistant,
  # and .gitkeep are preserved because tar archives the complete directory.
  tar_excludes=()
  for pattern in "${excludes[@]}"; do
    tar_excludes+=("--exclude=./$pattern")
  done
  (
    cd "$source_dir"
    tar "${tar_excludes[@]}" -cf - .
  ) | (
    cd "$target_dir"
    tar -xf -
  )
fi

if ((dry_run)); then
  printf '[create-project] Dry run complete; no files were copied.\n'
else
  printf '[create-project] Template copied successfully.\n'
  printf '[create-project] Next: edit config/ai-project.yaml and run ./scripts/bootstrap.sh\n'
fi
