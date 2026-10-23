#!/bin/sh
# Reproduce the Part 4 decoding evidence and gate check.
#
#   reports/part4-decoding/reproduce.sh [OUTPUT_DIR]
#
# Prerequisites as for reports/part2-baseline/reproduce.sh: CMake, a C++11
# compiler, the pinned interpreters (harness/setup_interpreters.sh) and a
# host CPython >= 3.10.  Every pycdas, pycdc and reference run happens in the
# harness sandbox; no .pyc is executed.
#
# Besides the current tree it builds the pre-Part-4 foundation (bootstrap
# 4d29eee, the Part 3 integration) and runs the same dis and malformed
# checks against it, as a control: dis must find the defects Part 4 fixed,
# and pycdc crashes on 3.10-3.12 must not increase.
#
# Expected (macOS arm64 reference host): compare regression 0; controls 0
# unexpected; upstream token suite PASS=191 FAIL=0 XFAIL=39 XPASS=0; dis,
# headers and formats without a single mismatch; malformed without a crash or
# hang in pycdas on any version or in pycdc on 3.13/3.14; gate --part 4
# PASSED.  It took 9 minutes on the reference host (18 parallel jobs).
set -eu
repo=$(cd "$(dirname "$0")/../.." && pwd)
out=${1:-$repo/build/part4-repro}
py=${PYTHON:-python3}
before=4d29eee8b57979c018a758284a17f6bfaeea2f0f
T=harness/tools/decoding_check.py
cd "$repo"
mkdir -p "$out"

"$py" harness/difftest.py interpreters || { echo "run harness/setup_interpreters.sh first"; exit 1; }
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release > "$out/cmake-release.log"
cmake --build build/release -j8 > "$out/build-release.log"
cmake -S . -B build/debug -DCMAKE_BUILD_TYPE=Debug > "$out/cmake-debug.log"
cmake --build build/debug -j8 > "$out/build-debug.log"
b="$out/before"
[ -d "$b" ] || git clone -q --shared --no-checkout . "$b"
git -C "$b" checkout -q --detach "$before"
cmake -S "$b" -B "$b/build" -DCMAKE_BUILD_TYPE=Release > "$out/cmake-before.log"
cmake --build "$b/build" -j8 > "$out/build-before.log"

"$py" $T generate --out build/decoding-generated
suites=features,upstream-inputs,decoding,decoding-generated
"$py" harness/difftest.py controls --workroot "$out/work-controls" \
    --out "$out/controls.json" --summary "$out/CONTROLS.md"
"$py" harness/difftest.py run --suite $suites --workroot "$out/work" \
    --out "$out/results.json" --summary "$out/SUMMARY.md"
"$py" harness/difftest.py run --suite $suites --pycdc build/debug/pycdc \
    --workroot "$out/work-debug" --out "$out/results-debug.json"
"$py" harness/tools/upstream_suite.py --build-dir build/release \
    --json "$out/upstream_per_file_outcomes.json" | grep totals

D="$out/decoding"
"$py" $T dis --workroot "$out/work" --suites $suites --workdir "$D" \
    --out "$D/dis.json" --summary "$D/DIS.md" > /dev/null || true
"$py" $T headers --workroot "$out/work" --suites features,decoding,decoding-generated \
    --workdir "$D" --out "$D/headers.json" > /dev/null || true
"$py" $T formats --workroot "$out/work" --workdir "$D" --out "$D/formats.json" > /dev/null || true
"$py" $T malformed --workroot "$out/work" --suites features,decoding --workdir "$D" \
    --out "$D/malformed.json" > "$D/malformed.txt" || true

# Control: the pre-Part-4 build on the same .pyc files and seeded inputs.
C="$out/decoding-before"
"$py" $T dis --workroot "$out/work" --suites $suites --workdir "$C" \
    --pycdas "$b/build/pycdas" --pycdc "$b/build/pycdc" \
    --out "$C/dis.json" --summary "$C/DIS.md" > /dev/null || true
"$py" $T formats --workroot "$out/work" --workdir "$C" \
    --pycdas "$b/build/pycdas" --pycdc "$b/build/pycdc" --out "$C/formats.json" > /dev/null || true
"$py" $T malformed --workroot "$out/work" --suites features,decoding --workdir "$C" \
    --pycdas "$b/build/pycdas" --pycdc "$b/build/pycdc" \
    --out "$C/malformed.json" > "$C/malformed.txt" || true

"$py" harness/difftest.py compare reports/part2-baseline/baseline.json "$out/results.json" \
    > "$out/compare.txt" || true
head -13 "$out/compare.txt"
"$py" harness/difftest.py compare "$out/results.json" "$out/results-debug.json" \
    > "$out/compare-debug.txt" || true
for p in 4 5 6 7; do
    "$py" harness/difftest.py gate --part $p --results "$out/results.json" \
        --controls "$out/controls.json" --upstream "$out/upstream_per_file_outcomes.json" \
        --decoding "$D" --limit 0 > "$out/gate-part$p.txt" || true
    tail -1 "$out/gate-part$p.txt"
done
echo "REPRODUCED: results in $out"
