#!/bin/sh
# vault-film setup: find or install the engines this skill builds with. Safe to re-run; it never overwrites films.
#   sh ~/.claude/skills/vault-film/setup.sh           check everything, create the Remotion workspace if missing
#   sh ~/.claude/skills/vault-film/setup.sh check     report only, install nothing
set -u
MODE=${1:-install}
SKILL=$(cd "$(dirname "$0")" && pwd -P)
MOTION=${VAULT_FILM_MOTION:-$(cd "$SKILL/../.." && pwd -P)/motion}
LEMO=${LEMO_OPUSCAR_HOME:-$HOME/lemo-opuscar}
TTS=$HOME/.venvs/hyperframes-tts/bin/python
ok() { printf '  ok       %s\n' "$1"; }
miss() { printf '  MISSING  %s\n' "$1"; MISSING=1; }
MISSING=0
echo "system tools"
for t in node npm ffmpeg ffprobe python3; do
  if command -v "$t" >/dev/null 2>&1; then ok "$t ($( ("$t" --version 2>/dev/null || "$t" -version 2>/dev/null) | head -1))"; else miss "$t: install it yourself (not installed by this script)"; fi
done
echo "voice (Kokoro)"
if [ -x "$TTS" ]; then ok "$TTS"; else miss "$TTS: python3 -m venv ~/.venvs/hyperframes-tts && ~/.venvs/hyperframes-tts/bin/pip install kokoro-onnx soundfile numpy, then npx hyperframes tts --help"; fi
echo "HyperFrames engine"
if HV=$(npx --no-install hyperframes --version 2>/dev/null || npx hyperframes --version 2>/dev/null); then ok "hyperframes $HV"; else miss "npx hyperframes (needs network the first time)"; fi
echo "canvas engine (Lemo-Opuscar library)"
if [ -f "$LEMO/core/render/video.mjs" ]; then
  ok "$LEMO"
  [ -d "$LEMO/node_modules" ] && ok "library node_modules" || miss "library deps: sh $LEMO/plugin/skills/lemo-opuscar/scripts/setup.sh deps"
  [ -x "$LEMO/.venv/bin/python" ] && ok "library .venv (score and foley synthesis)" || miss "library .venv: sh $LEMO/plugin/skills/lemo-opuscar/scripts/setup.sh deps"
elif [ "$MODE" = check ]; then miss "$LEMO: git clone https://github.com/lemomo-ai/lemo-opuscar $LEMO"
else
  echo "  cloning the Lemo-Opuscar library to $LEMO"
  git clone --depth 1 https://github.com/lemomo-ai/lemo-opuscar "$LEMO" && sh "$LEMO/plugin/skills/lemo-opuscar/scripts/setup.sh" deps && ok "$LEMO" || miss "clone or deps failed: $LEMO"
fi
echo "Remotion engine (shared workspace)"
if [ ! -f "$MOTION/package.json" ]; then
  if [ "$MODE" = check ]; then miss "$MOTION: run setup.sh without 'check' to create it"
  else mkdir -p "$MOTION" && cp -R "$SKILL/templates/remotion/workspace/." "$MOTION/" && mkdir -p "$MOTION/src/films" && echo "  created $MOTION"; fi
fi
if [ -f "$MOTION/package.json" ]; then
  if [ ! -d "$MOTION/node_modules/remotion" ]; then
    if [ "$MODE" = check ]; then miss "$MOTION/node_modules: cd $MOTION && npm install"
    else echo "  npm install in $MOTION (a few minutes the first time)"; (cd "$MOTION" && npm install --no-audit --no-fund >/dev/null 2>&1) || miss "npm install failed in $MOTION"; fi
  fi
  [ -d "$MOTION/node_modules/remotion" ] && ok "$MOTION (remotion $(node -p "require('$MOTION/node_modules/remotion/package.json').version" 2>/dev/null))"
  # components added to the skill later reach an existing workspace without touching files that are already there
  for f in "$SKILL"/templates/remotion/workspace/src/lib/*; do [ -e "$MOTION/src/lib/$(basename "$f")" ] || { [ "$MODE" = check ] || cp "$f" "$MOTION/src/lib/"; }; done
fi
echo "skill link"
[ -e "$HOME/.claude/skills/vault-film" ] && ok "~/.claude/skills/vault-film" || { [ "$MODE" = check ] && miss "~/.claude/skills/vault-film" || { ln -s "$SKILL" "$HOME/.claude/skills/vault-film" && ok "linked ~/.claude/skills/vault-film"; }; }
[ "$MISSING" = 0 ] && echo "all engines found" || { echo "some engines are missing (see MISSING lines)"; exit 1; }
