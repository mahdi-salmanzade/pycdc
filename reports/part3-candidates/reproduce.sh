#!/bin/sh
# Reproduce the Part 3 candidate evaluation (upstream PRs #616 and #617) and
# the measurement of the integrated foundation.
#
#   reports/part3-candidates/reproduce.sh [OUTPUT_DIR]
#
# Prerequisites as for reports/part2-baseline/reproduce.sh (CMake, a C++11
# compiler, the pinned interpreters from harness/setup_interpreters.sh, a
# CPython >= 3.10 host), plus network access to fetch the two pull requests
# from github.com/zrax/pycdc.  Every candidate binary and every recovered
# program runs inside the harness sandbox; contributor test inputs are only
# compiled and decompiled, never executed.
#
# Expected: the candidate heads below; base identical to the Part 2
# baseline; the counts in reports/part3-candidates/COMPARISON.md; upstream
# token suite PASS=191 FAIL=0 XFAIL=39 XPASS=0 for every build; for the
# integrated build `compare` reports regression 0, and gate --part 4 reports
# 429/429 cases at disassemble with exactly 4 problems (the 4 Part 4
# requirements that are not mechanized yet).  PR #616's crash on
# loops/nested_exits varies between runs (see README.md).
set -eu
repo=$(cd "$(dirname "$0")/../.." && pwd)
out=${1:-$repo/build/part3-repro}
py=${PYTHON:-python3}
base=b4289760970dbc399684f1e155ec6d1ea1cc787e
pr616=e3936f875ad069c97cfc3ce136dfce9f4499f9c5
pr617=88e988be8ecc394b5a48d5686b60e19b6d4d5d2c
cd "$repo"
mkdir -p "$out/src" "$out/results"

git fetch upstream "+refs/pull/616/head:refs/remotes/upstream/pr/616" \
    "+refs/pull/617/head:refs/remotes/upstream/pr/617"
for spec in "pr616 $pr616" "pr617 $pr617"; do
    set -- $spec
    got=$(git rev-parse "upstream/pr/${1#pr}")
    [ "$got" = "$2" ] || echo "NOTE: PR ${1#pr} head is now $got (evaluated: $2)"
done

"$py" harness/difftest.py interpreters || { echo "run harness/setup_interpreters.sh first"; exit 1; }

# Each candidate is a detached clone at its exact commit, built the same way.
for spec in "base $base" "pr616 $pr616" "pr617 $pr617"; do
    set -- $spec
    d="$out/src/$1"
    [ -d "$d" ] || git clone -q --shared --no-checkout . "$d"
    git -C "$d" checkout -q --detach "$2"
    cmake -S "$d" -B "$d/build" -DCMAKE_BUILD_TYPE=Release > "$out/$1.cmake.log"
    cmake --build "$d/build" -j8 > "$out/$1.build.log"
done
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release > "$out/integrated.cmake.log"
cmake --build build/release -j8 > "$out/integrated.build.log"

# Frozen corpus (features + upstream inputs) and upstream's token suite.
for name in base pr616 pr617; do
    "$py" harness/difftest.py run --suite features,upstream-inputs \
        --pycdc "$out/src/$name/build/pycdc" --source-root "$out/src/$name" \
        --workroot "$out/work-$name" --out "$out/results/$name.json"
    "$py" harness/tools/upstream_suite.py --build-dir "$out/src/$name/build" \
        --json "$out/results/$name.upstream.json" | grep totals
done
"$py" harness/difftest.py run --suite features,upstream-inputs \
    --workroot "$out/work-integrated" --out "$out/results/integrated.json"
"$py" harness/tools/upstream_suite.py --build-dir build/release \
    --json "$out/results/integrated.upstream.json" | grep totals
"$py" harness/difftest.py controls --workroot "$out/work-controls" \
    --out "$out/results/controls.json"

# Contributor test inputs: compiled and decompiled only (L1), 3.13 and 3.14.
mkdir -p "$out/contrib/pr616"
cp "$out/src/pr616/tests/py314_roundtrip/cases/"*.py "$out/contrib/pr616/"
"$py" -I reports/part3-candidates/extract_pr617_cases.py \
    "$out/src/pr617/tests/modern_roundtrip.py" "$out/contrib/pr617"
for name in base pr616 pr617 integrated; do
    if [ "$name" = integrated ]; then exe=build/release/pycdc; srcroot=.;
    else exe="$out/src/$name/build/pycdc"; srcroot="$out/src/$name"; fi
    "$py" harness/difftest.py run --versions 3.13,3.14 \
        --suite "contrib-pr616=$out/contrib/pr616,contrib-pr617=$out/contrib/pr617" \
        --pycdc "$exe" --source-root "$srcroot" --workroot "$out/work-contrib-$name" \
        --out "$out/results/contrib-$name.json"
done

# Opcode tables versus each pinned interpreter's dis.opmap.
for name in base pr616 pr617; do
    "$py" harness/tools/opcode_coverage.py --pyc-root "$out/work-$name/features" \
        --source-root "$out/src/$name" --workdir "$out/opcodes-$name" \
        --out "$out/results/$name.opcodes.md"
done
"$py" harness/tools/opcode_coverage.py --pyc-root "$out/work-integrated/features" \
    --workdir "$out/opcodes-integrated" --out "$out/results/integrated.opcodes.md"

# Reports.
B=reports/part2-baseline/baseline.json
r="$out/results"
"$py" harness/tools/candidate_compare.py --baseline $B base="$r/base.json" \
    pr616="$r/pr616.json" pr617="$r/pr617.json" integrated="$r/integrated.json" \
    --json "$r/comparison.json" --limit 400 > "$r/COMPARISON.md"
"$py" harness/tools/candidate_compare.py --baseline "$r/contrib-base.json" \
    pr616="$r/contrib-pr616.json" pr617="$r/contrib-pr617.json" \
    integrated="$r/contrib-integrated.json" > "$r/CONTRIB.md"
"$py" harness/difftest.py compare $B "$r/integrated.json" | tee "$r/integrated.compare.txt"
for p in 4 5 6 7; do
    "$py" harness/difftest.py gate --part $p --results "$r/integrated.json" \
        --controls "$r/controls.json" --upstream "$r/integrated.upstream.json" \
        --limit 0 > "$r/gate-part$p.txt" || true
    tail -1 "$r/gate-part$p.txt"
done
echo "REPRODUCED: results in $r; compare its comparison.json with reports/part3-candidates/"
