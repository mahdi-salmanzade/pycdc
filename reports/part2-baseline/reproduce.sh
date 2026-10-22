#!/bin/sh
# Reproduce the Part 2 frozen baseline from scratch and compare it with the
# committed one.  Prerequisites: CMake, a C++11 compiler, uv (for
# harness/setup_interpreters.sh) and any CPython >= 3.10 as the host.
#
#   reports/part2-baseline/reproduce.sh [OUTPUT_DIR]
#
# Expected: interpreters all "ok", 0 unexpected control outcomes, upstream
# token suite PASS=191 FAIL=0 XFAIL=39 XPASS=0, and a compare with
# regression/missing_coverage/harness_error/corpus_drift all 0.  On a host
# other than macOS arm64 the sandbox is unavailable (pass the flags shown by
# difftest.py) and .pyc hashes may differ (corpus_drift is then expected).
set -eu
repo=$(cd "$(dirname "$0")/../.." && pwd)
out=${1:-$repo/build/part2-repro}
py=${PYTHON:-python3}
cd "$repo"
mkdir -p "$out"

"$py" harness/difftest.py interpreters || { echo "run harness/setup_interpreters.sh first"; exit 1; }
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release > "$out/cmake-configure.log"
cmake --build build/release -j8 > "$out/cmake-build.log"

"$py" harness/difftest.py controls --workroot build/difftest-repro-controls \
    --out "$out/controls.json" --summary "$out/CONTROLS.md"
"$py" harness/difftest.py run --suite features,upstream-inputs --workroot build/difftest-repro \
    --out "$out/results.json" --summary "$out/SUMMARY.md"
(cd build/release && "$py" -I ../../reports/part1-baseline/per_file_outcomes.py \
    --json "$out/upstream_per_file_outcomes.json")
"$py" harness/difftest.py compare reports/part2-baseline/baseline.json "$out/results.json" \
    | tee "$out/compare.txt"
echo "REPRODUCED: results in $out"
