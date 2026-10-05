#!/usr/bin/env bash
# Build an AppImage for OpenBI Desktop.
#
# Prerequisites:
#   - venv active with pyinstaller installed
#   - packaging/tools/appimagetool-x86_64.AppImage present
#
# Produces: OpenBI-Desktop-<version>-x86_64.AppImage in the repo root.

set -euo pipefail

cd "$(dirname "$0")/.."
VERSION="${VERSION:-0.1.0}"

echo "==> Cleaning previous build"
rm -rf build dist packaging/AppDir
rm -f ./*.AppImage

echo "==> PyInstaller"
pyinstaller packaging/openbi-desktop.spec --noconfirm --clean

echo "==> Assembling AppDir"
mkdir -p packaging/AppDir/usr/bin
mkdir -p packaging/AppDir/usr/share/applications
mkdir -p packaging/AppDir/usr/share/icons/hicolor

cp -r dist/openbi-desktop/* packaging/AppDir/usr/bin/
cp packaging/openbi-desktop.desktop packaging/AppDir/
cp packaging/openbi-desktop.desktop packaging/AppDir/usr/share/applications/
cp -r src/openbi_desktop/resources/icons/hicolor/* packaging/AppDir/usr/share/icons/hicolor/
cp src/openbi_desktop/resources/icons/hicolor/256x256/apps/openbi-desktop.png \
   packaging/AppDir/openbi-desktop.png

cat > packaging/AppDir/AppRun << 'APPRUN'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/openbi-desktop" "$@"
APPRUN
chmod +x packaging/AppDir/AppRun

echo "==> appimagetool"
ARCH=x86_64 ./packaging/tools/appimagetool-x86_64.AppImage packaging/AppDir

echo "==> Renaming and checksumming"
FINAL="OpenBI-Desktop-${VERSION}-x86_64.AppImage"
mv OpenBI_Desktop-x86_64.AppImage "$FINAL"
sha256sum "$FINAL" > "${FINAL}.sha256"

echo
echo "Built: $FINAL"
cat "${FINAL}.sha256"
