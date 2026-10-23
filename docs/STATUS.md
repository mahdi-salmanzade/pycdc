# Status

**Current part:** 4, make bytecode decoding trustworthy.

**Status:** READY_FOR_REVIEW.
- The mechanized gate (`gate --part 4`) passes.
- Six production commits need an independent review, so this is not
  COMPLETE.

**Authorized next action:**
- Hand `docs/HANDOFF.md` to the reviewing models.
- Part 5 is **not** authorized until the user says "continue".

**Earlier parts:**

| Part | Status | Note |
| --- | --- | --- |
| 1 | COMPLETE | gate passed 2026-10-22 |
| 2 | READY_FOR_REVIEW | independent reproduction and review outstanding |
| 3 | READY_FOR_REVIEW | independent review of `200a4cd`/`27ef3c6` outstanding |

Parts 3 and 4 started on the user's "continue" while the earlier reviews
were outstanding (D-013, D-017). No review is claimed for any part.

## Part 4 gate checklist

| Gate item | State | Evidence |
| --- | --- | --- |
| Required decoding fixtures match the reference at the defined semantic level | done | `reports/part4-decoding/decoding/DIS.md`: pycdas equals `marshal`/`dis` on 1,953/1,953 files (`features`, `upstream-inputs`, `decoding`, `decoding-generated`; 3.10–3.14; `-O0/1/2`). The same check on the pre-Part-4 build finds 684 mismatching files. |
| Unsupported formats fail clearly | done | `decoding/formats.json`: 17 crafted inputs × 2 tools, all exit 1 with a message. The pre-Part-4 pycdas exited 0 on 6. |
| Malformed inputs fail safely | done, for the defined scope | `decoding/malformed.txt`: 62,586 derived inputs per tool. pycdas has 0 crashes or hangs on every version; pycdc has 0 on 3.13/3.14. pycdc on 3.10–3.12: 51 crashes or hangs, all present in the pre-Part-4 build (52). D-019 limits pycdc's requirement to 3.13/3.14; this needs ASTRA's confirmation. |
| Hash-based headers | done | `decoding/headers.json`: 1,128/1,128 identical |
| Existing covered versions do not regress | done | `compare.txt`: regression 0. Outcomes identical to the Part 3 foundation. Upstream token suite 191/39 per file. Controls 0 unexpected. Debug = Release. |
| Independent review | **pending** | — |
| `gate --part 4` | PASSED | `reports/part4-decoding/gate-part4.txt` |

## Foundation in one line

`bootstrap` at the commit containing this file is the Part 3 foundation plus
verified decoding.
- pycdas matches CPython's own decoding on the whole corpus for 3.10–3.14.
- Constants are rendered exactly.
- Undecodable input fails clearly.
- Behavioral passes are unchanged: 15/15/9 on 3.10/3.11/3.12, 0 on 3.13 and
  3.14.
