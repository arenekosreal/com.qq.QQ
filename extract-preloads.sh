#!/usr/bin/bash

JQ=${JQ:-jq -r}
CURL=${CURL:-curl}
FLATPAK=${FLATPAK:-flatpak}
FLATPAK_BUILDER=${FLATPAK_BUILDER:-flatpak-builder}
BSDTAR=${BSDTAR:-bsdtar}
AWK=${AWK:-awk}
SHA256SUM=${SHA256SUM:-sha256sum}
ECHO=${ECHO:-echo}
RM=${RM:-rm -rf}
SED=${SED:-sed -i}
EXIT=${EXIT:-exit}
WC=${WC:-wc -l}
FIND=${FIND:-find}
CUT=${CUT:-cut}
REALPATH=${REALPATH:-realpath}
DIRNAME=${DIRNAME:-dirname}
LN=${LN:-ln -srfv}
MKTEMP=${MKTEMP:-mktemp -d}
# FLATPAK_BUILDER_ARGS
BUILD_DIR=${BUILD_DIR:-build}
MANIFEST=${MANIFEST:-com.qq.QQ.yaml}

declare _ARCH
_ARCH=$($FLATPAK --default-arch)

declare _JQ_EXTRA_SELECTOR=".modules[].sources | map(select(.type == \"extra-data\")) | select(length > 0)"
declare _JQ_ARCH_SELECTOR="map(select(.\"only-arches\" | contains([\"$_ARCH\"])))"
declare _JQ_ITEM_SELECTOR="$_JQ_EXTRA_SELECTOR | $_JQ_ARCH_SELECTOR | .[0]"
declare _JQ_URL_SELECTOR=" $_JQ_ITEM_SELECTOR | .url"
declare _JQ_SHA256_SELECTOR="$_JQ_ITEM_SELECTOR | .sha256"

declare _MANIFEST_JSON _URL _TMP_QQ_VERSION _SHA256_VALUE
_MANIFEST_JSON=$($FLATPAK_BUILDER --show-manifest "$MANIFEST")
_URL=$($ECHO "$_MANIFEST_JSON" | $JQ "$_JQ_URL_SELECTOR")
_SHA256_VALUE=$($ECHO "$_MANIFEST_JSON" | $JQ "$_JQ_SHA256_SELECTOR")
_TMP_QQ_VERSION=$($ECHO "${_URL##*/}" | $CUT -d _ -f 2,3)
declare _TMP_QQ_DEB="qq-$_TMP_QQ_VERSION.deb"

if [[ -f "$_TMP_QQ_DEB" ]]
then
    declare _SHA256_VALUE_ACTUAL
    _SHA256_VALUE_ACTUAL=$($SHA256SUM "$_TMP_QQ_DEB" | $AWK "{print \$1}")
    if [[ "$_SHA256_VALUE_ACTUAL" != "$_SHA256_VALUE" ]]
    then
        $ECHO "SHA256 Checksum mismatch:"
        $ECHO "Wants $_SHA256_VALUE"
        $ECHO "Actual $_SHA256_VALUE_ACTUAL"
        $ECHO
        $ECHO "Removing $_TMP_QQ_DEB..."
        $RM "$_TMP_QQ_DEB"
    fi
fi

if [[ ! -f "$_TMP_QQ_DEB" ]]
then
    $ECHO "Downloading $_TMP_QQ_DEB with URL $_URL..."
    $CURL -L "$_URL" -o "$_TMP_QQ_DEB"
fi

$ECHO "Extracting $_TMP_QQ_DEB..."
$BSDTAR --to-stdout -xf "$_TMP_QQ_DEB" "data.*" | $BSDTAR -xf -

declare _TMP_QQ_DIR="opt/QQ"
declare _TMP_QQ_RESOURCES="$_TMP_QQ_DIR/resources/app"
declare _TMP_QQ_INDEX_JS="$_TMP_QQ_RESOURCES/app_launcher/index.js"
declare _TMP_REPO
_TMP_REPO=$($REALPATH "$($DIRNAME "$0")")
declare _TMP_REPO_EXTRACTOR_JS="$_TMP_REPO/patch/extractor.js"
$ECHO "Modifying $_TMP_QQ_INDEX_JS..."
$SED "1 i require(\"$_TMP_REPO_EXTRACTOR_JS\");" "$_TMP_QQ_INDEX_JS"

declare _TMP_REPO_PRELOADS_DIR="$_TMP_REPO/preloads"
$ECHO "Removing $_TMP_REPO_PRELOADS_DIR folder..."
$RM "$_TMP_REPO_PRELOADS_DIR"

$ECHO "Launching modified QQ..."
declare _TMP_QQ_HOME
_TMP_QQ_HOME=$($MKTEMP)
HOME="$_TMP_QQ_HOME" "$_TMP_QQ_DIR/qq" --no-sandbox "$_TMP_QQ_RESOURCES"

if [[ ! -d "$_TMP_REPO_PRELOADS_DIR" ]]
then
    $ECHO "Failed to extract preloads."
    $EXIT 1
fi

declare _TMP_PRELOADS_COUNT
_TMP_PRELOADS_COUNT=$($FIND "$_TMP_REPO_PRELOADS_DIR" -type f -name "*preload*.js" | $WC)
if [[ "$_TMP_PRELOADS_COUNT" -gt 0 ]]
then
    declare _TMP_PRELOADS_ARCHIVE="$_TMP_REPO/preloads-$_TMP_QQ_VERSION.tar.gz"
    declare _TMP_PRELOADS_ARCHIVE_NO_VERSION="$_TMP_REPO/preloads.tar.gz"
    $ECHO "Extract preloads successfully."
    $ECHO "Creating archive..."
    $BSDTAR -C "$_TMP_REPO" -cf "$_TMP_PRELOADS_ARCHIVE" "$($REALPATH --relative-to="$_TMP_REPO" "$_TMP_REPO_PRELOADS_DIR")"
    $LN "$_TMP_PRELOADS_ARCHIVE" "$_TMP_PRELOADS_ARCHIVE_NO_VERSION"
    $ECHO "Cleaning up temp files..."
    $RM "$_TMP_QQ_DEB" "opt" "usr" "$_TMP_REPO_PRELOADS_DIR"
    $RM "$_TMP_QQ_HOME"
    $EXIT 0
fi

$ECHO "No preload js found."
$EXIT 1
