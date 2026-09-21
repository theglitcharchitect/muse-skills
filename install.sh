#!/usr/bin/env bash
#
# muse-skills one-command installer.
#
# Installs the Jev decision layer (skills/jev-router) plus the full skill
# library into your Muse skills directory, and keeps a local clone of the
# repo (demo + docs) for reference.
#
#   curl -fsSL https://raw.githubusercontent.com/theglitcharchitect/muse-skills/main/install.sh | bash
#
# Existing skills with the same names are replaced; nothing else on the
# machine is touched. Override locations with MUSE_SKILLS_DIR and
# MUSE_SKILLS_DEST.
#
set -euo pipefail

REPO_URL="https://github.com/theglitcharchitect/muse-skills.git"
BRANCH="main"
CLONE_DIR="${MUSE_SKILLS_DIR:-$HOME/workspace/muse-skills}"
SKILLS_DIR="${MUSE_SKILLS_DEST:-$HOME/workspace/skills}"

need() { command -v "$1" >/dev/null 2>&1 || { echo "error: '$1' is required but not installed." >&2; exit 1; }; }
need git
need python3

if [ -d "$CLONE_DIR/.git" ]; then
  echo ">> updating existing clone at $CLONE_DIR"
  git -C "$CLONE_DIR" pull --ff-only --quiet 2>/dev/null || \
    echo ">> note: could not fast-forward $CLONE_DIR, using what is there"
else
  echo ">> cloning muse-skills to $CLONE_DIR"
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$CLONE_DIR" --quiet
fi

mkdir -p "$SKILLS_DIR"
n=0
for skill in "$CLONE_DIR"/skills/*/; do
  [ -d "$skill" ] || continue
  name="$(basename "$skill")"
  rm -rf "$SKILLS_DIR/$name"
  cp -r "$skill" "$SKILLS_DIR/$name"
  n=$((n + 1))
done

echo ">> installed $n skills -> $SKILLS_DIR"
echo
echo "Try the demo (no key needed, runs in mock mode):"
echo "  cd $CLONE_DIR && python3 demo/run.py"
echo
echo "Go live (Jev evaluates through the Vercel AI Gateway, free tier):"
echo "  export VERCEL_AI_GATEWAY_KEY=<your key>"
echo "  cd $CLONE_DIR && python3 demo/run.py"
echo
echo "Keep the shadow log before trusting active mode: docs/shadow-mode.md"
