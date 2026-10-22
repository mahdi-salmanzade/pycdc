#!/bin/sh
# Install the pinned CPython interpreters listed in harness/interpreters.json
# with uv (python-build-standalone builds) into an isolated directory.
#
# --no-bin keeps uv from adding python3.x links to ~/.local/bin, and the
# separate install dir keeps uv's per-minor links for the user's own
# interpreters untouched.  Needs network access once, to download.
#
# Override the location with PYCDC_HARNESS_PYTHONS (and pass the same value
# to difftest.py --install-dir).
set -eu
here=$(cd "$(dirname "$0")" && pwd)
: "${PYCDC_HARNESS_PYTHONS:=$HOME/.cache/pycdc-harness/python}"
versions=$(python3 -c 'import json,sys; c=json.load(open(sys.argv[1])); print(" ".join(v["version"] for v in c["interpreters"].values()))' "$here/interpreters.json")
echo "installing $versions into $PYCDC_HARNESS_PYTHONS"
UV_PYTHON_INSTALL_DIR="$PYCDC_HARNESS_PYTHONS" uv python install --no-bin $versions
