#!/bin/bash
# Builds the Outspoken review site from an immutable commit of the public repository,
# then overlays the pre-uploaded media that the public commit does not carry.
set -euo pipefail
SHA="${SHA:?set SHA to the commit of mcharniuk1-spec/linkedin to deploy}"
WORK="$(mktemp -d)"
curl -fsSL --retry 3 "https://codeload.github.com/mcharniuk1-spec/linkedin/tar.gz/$SHA" | tar -xz -C "$WORK" --strip-components=1 "linkedin-$SHA/design and website"
SRC="$WORK/design and website/website"
( cd "$SRC" && npm ci --ignore-scripts --no-audit --no-fund && npm run build )
DIST="$SRC/dist"
rm -rf site && mkdir -p site
cp -R assets site/assets
cp -R video site/video
cp "$DIST/index.html" site/index.html
cp "$DIST"/assets/index-* site/assets/
for p in assets/identity/font-source/fraunces assets/identity/font-source/mona-sans assets/identity/font-source/geist-mono assets/revisions/v10/people/maksym-charniuk.jpg assets/revisions/v10/people/mykhailo-amplieiev.jpg assets/revisions/v5/identity/wordmark-marigold.svg assets/revisions/v5/identity/lockup-marigold.svg; do
  mkdir -p "site/$(dirname "$p")"
  cp -R "$DIST/$p" "site/$p"
done
cd site
grep -ohE '/(assets|video)/[A-Za-z0-9_./%,-]+\.(js|css|svg|png|jpg|webp|woff2|ttf|mp4|glb)' index.html assets/index-* | sort -u | while read -r p; do
  f="${p#/}"; f="$(printf '%b' "${f//%/\\x}")"
  [ -f "$f" ] || { echo "MISSING $f"; exit 1; }
done
echo "site files: $(find . -type f | wc -l)"
