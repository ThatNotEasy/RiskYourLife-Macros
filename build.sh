#!/usr/bin/env bash
set -euo pipefail

# =========================
# Config
# =========================
APP_NAME="main"                 # entry script WITHOUT .py (i.e., main.py)
PY_CMD="${PYTHON:-python}"      # override with: PYTHON=/path/to/python bash build.sh
ICON="assets/rylm_circular.ico"

# Output filename for the exe
OUT_NAME="RiskYourLife-Macros.exe"

# Windows version info / metadata
PRODUCT_NAME="RiskYourLife-Macros"
FILE_DESC="Compatible with All Kind of RiskYourLife"
COMPANY="Pari Malam"
FILE_VER="2.1"      # must be 4-part
PRODUCT_VER="2.1"   # make product version 4-part too
COPYRIGHT="(c) 2025 Pari Malam"

NUITKA_FLAGS=(
  --onefile --follow-imports --lto=yes --mingw64
  --windows-icon-from-ico="$ICON"
  --windows-product-name="$PRODUCT_NAME"
  --windows-file-description="$FILE_DESC"
  --windows-company-name="$COMPANY"
  --windows-file-version="$FILE_VER"
  --windows-product-version="$PRODUCT_VER"
  --copyright="$COPYRIGHT"
  --include-module=PIL.ImageQt \
  --include-module=psutil \
  --include-module=PyQt5
  --output-filename="$OUT_NAME"
)

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

# On Windows (Git Bash/MSYS), check if MinGW64 environment is ready
UNAME="$(uname -s || true)"
if [[ "$UNAME" == MINGW* || "$UNAME" == MSYS* || "$UNAME" == CYGWIN* || "$UNAME" == "Windows_NT" ]]; then
  if ! command -v gcc >/dev/null 2>&1; then
    info "MinGW64 (gcc) is not on PATH. Nuitka will download MinGW64 automatically."
  else
    ok "MinGW64 toolchain detected (gcc found)."
  fi
fi

# =========================
# Clean previous builds
# =========================
ARCHIVE_NAME="RiskYourLife-Macros_V${FILE_VER}.zip"

for path in \
  "${APP_NAME}.build" \
  "${APP_NAME}.dist" \
  "${APP_NAME}.onefile-build" \
  "nuitka-crash-report.xml" \
  "$OUT_NAME" \
  "$ARCHIVE_NAME"
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
# Result & Archive
# =========================
if [[ -f "$OUT_NAME" ]]; then
  ok "Build succeeded → ./$OUT_NAME"

  # Create versioned zip archive
  info "Creating archive: $ARCHIVE_NAME"

  # Use 7z command
  if command -v 7z >/dev/null 2>&1; then
    # Build list of files to include
    FILES_TO_ARCHIVE="$OUT_NAME"

    # Check for config files and add them if they exist
    ARCHIVE_CONTENTS="$OUT_NAME"
    if [[ -f "config.ini" ]]; then
      FILES_TO_ARCHIVE="$FILES_TO_ARCHIVE config.ini"
      ARCHIVE_CONTENTS="$ARCHIVE_CONTENTS and config.ini"
    fi

    if [[ -f "position.ini" ]]; then
      FILES_TO_ARCHIVE="$FILES_TO_ARCHIVE position.ini"
      ARCHIVE_CONTENTS="$ARCHIVE_CONTENTS and position.ini"
    fi

    # Create archive with all files
    7z a "$ARCHIVE_NAME" $FILES_TO_ARCHIVE

    if [[ -f "$ARCHIVE_NAME" ]]; then
      ok "Archive created → ./$ARCHIVE_NAME (includes $ARCHIVE_CONTENTS)"

      # Clean up build folders after successful archive
      info "Cleaning up build folders..."
      for path in \
        "${APP_NAME}.build" \
        "${APP_NAME}.dist" \
        "${APP_NAME}.onefile-build"
      do
        if [[ -e "$path" ]]; then
          info "Removing: $path"
          rm -rf "$path"
        else
          info "Skip (not found): $path"
        fi
      done
      ok "Build folder cleanup complete."
    else
      warn "Failed to create archive"
    fi
  else
    warn "7z command not found. Skipping archive creation."
    warn "Install 7-Zip and make sure 7z is in your PATH."
  fi
else
  warn "EXE not found as '$OUT_NAME'. Check for errors above or in *.dist/ folders."
fi

# --- GitHub CLI upload ---
REPO="ThatNotEasy/RiskYourLife-Macros"          # e.g. PariMalam/RiskYourLife
TAG="V${FILE_VER}"
RELEASE_TITLE="${PRODUCT_NAME} ${TAG}"
RELEASE_NOTES="Release ${TAG} — automated upload from build script."

if command -v gh >/dev/null 2>&1; then
  info "Creating/updating GitHub release $TAG and uploading $ARCHIVE_NAME with gh"
  # create release (will fail if release exists) — use --prerelease if desired
  gh release create "$TAG" "./$ARCHIVE_NAME" \
    --repo "$REPO" \
    --title "$RELEASE_TITLE" \
    --notes "$RELEASE_NOTES" \
    --draft=false || {
      # if release exists fallback to upload asset to existing release
      info "Release creation failed (may already exist). Uploading to existing release..."
      gh release upload "$TAG" "./$ARCHIVE_NAME" --repo "$REPO" --clobber
    }
  ok "Uploaded to GitHub Releases via gh."
else
  warn "gh CLI not found. Install GitHub CLI or use the curl method below."
fi