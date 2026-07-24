#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./.ai/tools/create-project.sh [--dry-run] [--force] <target-directory>
  ./.ai/tools/create-project.sh --update [--dry-run] [--apply] [--patch-file <path>] <target-directory>

Create mode copies reusable project scaffolding into an empty target without the
template repository, tests, history, tooling, temporary work, IDE, environment,
cache, or build state. Bootstrap is a separate, explicit step.

Update mode integrates template changes into an existing template-based project.
It adds new template files, refreshes reusable control-plane files, and never
overwrites project-owned files (see the [update_protected] manifest section) or
deletes anything in the target. By default it writes a reviewable patch and leaves
the target untouched; use --apply to write the safe changes directly.

Options:
  --update            Integrate template changes into an existing project.
  --apply             In update mode, write the safe changes instead of only a patch.
  --patch-file <path> In update mode, patch output path (default: template-update.patch).
  --dry-run           Preview only. Create mode requires rsync; update mode writes nothing.
  --force             Create mode only: allow overwriting same-named files in a non-empty target.
  -h, --help          Show this help.
USAGE
}

mode="create"
dry_run=0
force=0
apply=0
patch_file="template-update.patch"
args=()
while (($#)); do
  case "$1" in
    --dry-run) dry_run=1 ;;
    --force) force=1 ;;
    --update) mode="update" ;;
    --apply) apply=1 ;;
    --patch-file)
      if (($# < 2)); then
        printf 'Option --patch-file requires a value.\n' >&2
        exit 2
      fi
      patch_file="$2"
      shift
      ;;
    --patch-file=*) patch_file="${1#*=}" ;;
    -h | --help)
      usage
      exit 0
      ;;
    --)
      shift
      args+=("$@")
      break
      ;;
    -*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *) args+=("$1") ;;
  esac
  shift
done
if ((${#args[@]} != 1)); then
  usage >&2
  exit 2
fi
if [[ "$mode" == "create" ]] && ((apply)); then
  printf -- '--apply is only valid together with --update.\n' >&2
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
mapfile -t update_protected < <(read_manifest_section update_protected)

# Decide whether a template-relative path is omitted from any copy or update.
is_excluded() {
  local rel="$1"
  local segment name directory path extension
  local -a segments
  IFS='/' read -ra segments <<<"$rel"
  for segment in "${segments[@]}"; do
    for name in "${state_names[@]}"; do
      [[ "$segment" == "$name" ]] && return 0
    done
  done
  for directory in "${root_directories[@]}"; do
    [[ "$rel" == "$directory" || "$rel" == "$directory"/* ]] && return 0
  done
  for path in "${excluded_paths[@]}"; do
    [[ "$rel" == "$path" ]] && return 0
  done
  for extension in "${state_file_extensions[@]}"; do
    [[ "$rel" == *"$extension" ]] && return 0
  done
  return 1
}

# Project-owned files are seeded once and never overwritten by update mode.
is_protected() {
  local rel="$1" path
  for path in "${update_protected[@]}"; do
    [[ "$rel" == "$path" ]] && return 0
  done
  return 1
}

run_create() {
  if [[ -d "$target_dir" && -n "$(find "$target_dir" -mindepth 1 -maxdepth 1 -print -quit 2>/dev/null)" && $force -ne 1 ]]; then
    printf 'Target directory is not empty: %s\nUse --force only for an intentional merge.\n' "$target_dir" >&2
    exit 2
  fi
  if ((dry_run == 0)); then
    mkdir -p "$target_dir"
  fi

  printf '[create-project] Source: %s\n[create-project] Target: %s\n' "$source_dir" "$target_dir"
  if command -v rsync >/dev/null 2>&1; then
    local -a command
    command=(rsync -a --itemize-changes)
    ((dry_run)) && command+=(--dry-run)
    local path name extension
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
    local -a tar_excludes
    tar_excludes=()
    local path name extension
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
    printf '# Current work\n\nNo active requirement.\n' >"${target_dir}/.ai/CURRENT_PLAN.md"
    printf '[create-project] Template copied successfully.\n'
    printf '[create-project] Next: edit .ai/project.yaml and run ./.ai/tools/bootstrap.sh\n'
  fi
}

# Emit a git-apply-compatible unified diff that turns the project file into the
# template file. Added files diff against /dev/null.
emit_patch() {
  local rel="$1" src="$source_dir/$1" dst="$target_dir/$1"
  if [[ -e "$dst" ]]; then
    diff -u -L "a/$rel" -L "b/$rel" -- "$dst" "$src" || true
  else
    diff -u -L /dev/null -L "b/$rel" -- /dev/null "$src" || true
  fi
}

print_list() {
  local title="$1"
  shift
  (($#)) || return 0
  printf '  %s:\n' "$title"
  local item
  for item in "$@"; do
    printf '    - %s\n' "$item"
  done
}

write_patch_file() {
  local out="$1"
  shift
  (($#)) || return 1
  : >"$out"
  local rel
  for rel in "$@"; do
    emit_patch "$rel" >>"$out"
  done
  return 0
}

run_update() {
  if [[ ! -d "$target_dir" ]]; then
    printf 'Update target does not exist: %s\n' "$target_dir" >&2
    exit 2
  fi
  if [[ ! -f "$target_dir/AGENTS.md" || ! -d "$target_dir/.ai" ]]; then
    printf 'Target does not look like a template-based project (missing AGENTS.md or .ai/): %s\n' "$target_dir" >&2
    printf 'Use create mode for a brand-new project.\n' >&2
    exit 2
  fi

  local -a added=() updated=() protected_diff=()
  local n_unchanged=0
  local abs rel dst
  while IFS= read -r -d '' abs; do
    rel="${abs#"$source_dir"/}"
    is_excluded "$rel" && continue
    dst="$target_dir/$rel"
    if [[ ! -e "$dst" ]]; then
      added+=("$rel")
    elif cmp -s "$abs" "$dst"; then
      n_unchanged=$((n_unchanged + 1))
    elif is_protected "$rel"; then
      protected_diff+=("$rel")
    else
      updated+=("$rel")
    fi
  done < <(find "$source_dir" -type f -print0)

  printf '[update] Source: %s\n[update] Target: %s\n' "$source_dir" "$target_dir"
  printf '[update] new: %d, changed: %d, protected conflicts: %d, unchanged: %d\n' \
    "${#added[@]}" "${#updated[@]}" "${#protected_diff[@]}" "$n_unchanged"
  print_list "New template files (added)" "${added[@]}"
  print_list "Changed template files (reusable, safe to update)" "${updated[@]}"
  print_list "Protected project files (differ; manual merge)" "${protected_diff[@]}"

  if ((dry_run)); then
    printf '[update] Dry run: no files written.\n'
    return 0
  fi

  if ((${#added[@]} + ${#updated[@]} + ${#protected_diff[@]} == 0)); then
    printf '[update] Project already matches the template. Nothing to do.\n'
    return 0
  fi

  if ! command -v diff >/dev/null 2>&1; then
    printf 'diff is required to generate update patches. Install diffutils.\n' >&2
    exit 2
  fi

  local manual_patch
  case "$patch_file" in
    *.patch) manual_patch="${patch_file%.patch}.manual.patch" ;;
    *) manual_patch="${patch_file}.manual" ;;
  esac

  if ((apply)); then
    for rel in "${added[@]}" "${updated[@]}"; do
      mkdir -p "$target_dir/$(dirname "$rel")"
      cp "$source_dir/$rel" "$target_dir/$rel"
    done
    printf '[update] Applied %d new and %d changed template files.\n' \
      "${#added[@]}" "${#updated[@]}"
  else
    if write_patch_file "$patch_file" "${added[@]}" "${updated[@]}"; then
      printf '[update] Wrote template patch: %s\n' "$patch_file"
      printf '[update] Review it, then apply with: git -C %q apply %q\n' "$target_dir" "$patch_file"
      printf '[update] Or re-run with --apply to integrate the safe changes directly.\n'
    fi
  fi

  if write_patch_file "$manual_patch" "${protected_diff[@]}"; then
    printf '[update] Protected files changed in the template. Merge these by hand: %s\n' "$manual_patch"
    printf '[update] These project-owned files were NOT modified.\n'
  fi
}

if [[ "$mode" == "create" ]]; then
  run_create
else
  run_update
fi
