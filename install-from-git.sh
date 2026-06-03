#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Install or update hermes-publish-html from this git checkout into one or more Hermes homes/profiles.

Usage:
  ./install-from-git.sh [--profile NAME]...
  ./install-from-git.sh [--hermes-home PATH]...
  ./install-from-git.sh

Options:
  --profile NAME       Install into ~/.hermes/profiles/NAME
  --hermes-home PATH   Install into an explicit Hermes home directory
  -h, --help           Show this help

Behavior:
  - with no arguments, installs into the default Hermes home: ~/.hermes
  - repeat --profile and/or --hermes-home to fan out to multiple targets
  - uses rsync --delete so updates replace stale files cleanly
EOF
}

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"
SKILL_REL="autonomous-ai-agents/hermes-publish-html"
SRC_DIR="$REPO_ROOT/$SKILL_REL"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "Source skill directory not found: $SRC_DIR" >&2
  exit 1
fi

profiles=()
hermes_homes=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      [[ $# -ge 2 ]] || { echo "--profile requires a value" >&2; exit 1; }
      profiles+=("$2")
      shift 2
      ;;
    --hermes-home)
      [[ $# -ge 2 ]] || { echo "--hermes-home requires a value" >&2; exit 1; }
      hermes_homes+=("$2")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ${#profiles[@]} -eq 0 && ${#hermes_homes[@]} -eq 0 ]]; then
  hermes_homes+=("$HOME/.hermes")
fi

install_into_home() {
  local hermes_home="$1"
  local dest_parent="$hermes_home/skills/autonomous-ai-agents"
  local dest_dir="$dest_parent/hermes-publish-html"

  mkdir -p "$dest_parent"
  rsync -a --delete "$SRC_DIR/" "$dest_dir/"
  chmod +x "$dest_dir/scripts/publish_html_page.py"

  echo "Installed into: $dest_dir"
}

if (( ${#profiles[@]} > 0 )); then
  for profile in "${profiles[@]}"; do
    install_into_home "$HOME/.hermes/profiles/$profile"
  done
fi

if (( ${#hermes_homes[@]} > 0 )); then
  for hermes_home in "${hermes_homes[@]}"; do
    install_into_home "$hermes_home"
  done
fi
