#!/usr/bin/env bash
set -euo pipefail

# =========================
# Config
# =========================
APP_NAME="main"                 # your entry script without .py
PY_CMD="${PYTHON:-python}"      # override with: PYTHON=/path/to/python bash build.sh
ICON="assets/rylm.ico"
NUITKA_FLAGS=(--onefile --follow-imports --lto=yes --msvc=latest --windows-icon-from-ico="$ICON")

# =========================
# Helpers (pretty output)
# =========================
info()  { echo -e "\033[1;34m[INFO]\033[0m  $*"; }
ok()    { echo -e "\033[1;32m[OK]\033[0m    $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m  $*"; }
err()   { echo -e "\033[1;31m[ERROR]\033[0m $*" >&2; }

# =========================
# Show environment
# =========================
info "Using Python: $($PY_CMD -c 'import sys; print(sys.executable)')"
info "Python ver  : $($PY_CMD -c 'import sys; print(sys.version.split()[0])')"

if ! $PY_CMD -m nuitka --version >/dev/null 2>&1; then
  err "Nuitka not found in this Python environment."
  echo "Try:  $PY_CMD -m pip install --upgrade pip nuitka"
  exit 1
fi
ok "Nuitka is installed."

# On Windows (Git Bash/MSYS), check if MSVC environment is ready
UNAME="$(uname -s || true)"
if [[ "$UNAME" == MINGW* || "$UNAME" == MSYS* || "$UNAME" == CYGWIN* || "$UNAME" == "Windows_NT" ]]; then
  if ! command -v cl.exe >/dev/null 2>&1; then
    warn "MSVC (cl.exe) is not on PATH. If this fails, open 'x64 Native Tools Command Prompt for VS' then run this script."
    warn "Alternatively, install Build Tools + Windows SDK, or switch toolchain (e.g. --clang / --mingw64)."
  else
    ok "MSVC toolchain detected (cl.exe found)."
  fi
fi

# =========================
# Clean previous builds
# =========================
for path in \
  "${APP_NAME}.build" \
  "${APP_NAME}.dist" \
  "${APP_NAME}.onefile-build" \
  "nuitka-crash-report.xml"
do
  if [[ -e "$path" ]]; then
    info "Removing: $path"
    rm -rf "$path"
  else
    info "Skip (not found): $path"
  fi
done
ok "Cleanup complete."

# =========================
# Build
# =========================
BUILD_CMD=( "$PY_CMD" -m nuitka "${APP_NAME}.py" "${NUITKA_FLAGS[@]}" )

info "Build command:"
echo "  ${BUILD_CMD[*]}"
echo

time "${BUILD_CMD[@]}"

# =========================
# Result
# =========================
if [[ -f "${APP_NAME}.exe" ]]; then
  ok "Build succeeded → ./${APP_NAME}.exe"
else
  # Nuitka sometimes places artifacts next to source; onefile should create ${APP_NAME}.exe
  warn "EXE not found in current dir. Check for errors above or in *.dist/ folders."
fi
