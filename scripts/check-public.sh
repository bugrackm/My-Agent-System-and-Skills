#!/usr/bin/env bash
# Pre-publish leak scan. Run from anywhere: scripts/check-public.sh
#
# 1. Built-in secret patterns (API keys, tokens, private keys, absolute home paths).
# 2. Personal terms from .public-blocklist (one regex per line, '#' comments).
#    That file is gitignored on purpose: the list of words you must never publish
#    should not itself be published.
#
# Exits 1 if anything matches.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

secret_patterns=(
  'sk-[A-Za-z0-9_-]{20,}'
  'ghp_[A-Za-z0-9]{20,}'
  'github_pat_[A-Za-z0-9_]{20,}'
  'AKIA[0-9A-Z]{16}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'BEGIN [A-Z ]*PRIVATE KEY'
  '/home/[a-z][a-z0-9_-]*/'
  '/Users/[A-Za-z][A-Za-z0-9_-]*/'
)

exclude=(--exclude-dir=.git --exclude-dir=node_modules --exclude=check-public.sh --exclude=.public-blocklist)
found=0

scan() {
  local label="$1" pattern="$2"
  if grep -rnIE -i "${exclude[@]}" -e "$pattern" . ; then
    echo "  ^ $label: $pattern" >&2
    found=1
  fi
}

for p in "${secret_patterns[@]}"; do
  scan "secret" "$p"
done

if [[ -f .public-blocklist ]]; then
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    scan "blocklist" "$line"
  done < .public-blocklist
else
  echo "note: no .public-blocklist file; only secret patterns were checked" >&2
fi

if (( found )); then
  echo "check-public: FAILED — remove the matches above before publishing" >&2
  exit 1
fi
echo "check-public: clean"
