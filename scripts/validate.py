"""Data integrity checks. CI runs this on every PR; a failure blocks the merge."""
import glob, sys, yaml

ERRORS, WARNINGS = [], []

VALID = {
    "autonomy_class": {"manual", "semi_autonomous", "fully_autonomous"},
    "economic_engine": {"session", "duty_cycle"},
    "status": {"current", "announced", "discontinued", "unreleased"},
    "confidence": {"measured", "published", "vendor", "assumed"},
    "capability": {"capable", "vendor_claimed", "conditional", "not_capable", None},
    "basis": {"ac_per_hr", "ac_per_day", "ac_per_week", "ac_managed_vendor", ""},
}
SURFACES = ["greens", "tees", "approaches", "fairways",
            "intermediate_rough", "primary_rough", "driving_range"]


def check(path):
    m = yaml.safe_load(open(path))
    mid = m.get("id", path)

    for field, allowed in [("autonomy_class", VALID["autonomy_class"]),
                           ("economic_engine", VALID["economic_engine"]),
                           ("status", VALID["status"])]:
        if m.get(field) not in allowed:
            ERRORS.append(f"{mid}: {field}={m.get(field)!r} not in {sorted(allowed)}")

    # a fully autonomous machine runs a duty cycle; a session engine implies an operator loop
    if m.get("autonomy_class") == "fully_autonomous" and m.get("economic_engine") != "duty_cycle":
        ERRORS.append(f"{mid}: fully_autonomous must use the duty_cycle engine")
    if m.get("autonomy_class") == "manual" and m.get("economic_engine") != "session":
        ERRORS.append(f"{mid}: manual must use the session engine")

    for s in SURFACES:
        v = m.get("capability", {}).get(s)
        if v not in VALID["capability"]:
            ERRORS.append(f"{mid}: capability.{s}={v!r} invalid")
    if m.get("capability", {}).get("greens") != "not_capable":
        ERRORS.append(f"{mid}: greens must be not_capable — no robotic option exists at greens HOC")

    prov = m.get("provenance", {})
    if prov.get("confidence") not in VALID["confidence"]:
        ERRORS.append(f"{mid}: provenance.confidence={prov.get('confidence')!r} invalid")
    if not prov.get("sources"):
        ERRORS.append(f"{mid}: no sources — every record needs provenance")
    for src in prov.get("sources") or []:
        if not src.get("url") or not src.get("accessed"):
            ERRORS.append(f"{mid}: a source is missing url or accessed date")
    if prov.get("dispute") and not prov.get("dispute_note"):
        ERRORS.append(f"{mid}: dispute=true requires a dispute_note")

    cap = m.get("capacity", {})
    if cap.get("basis") not in VALID["basis"]:
        ERRORS.append(f"{mid}: capacity.basis={cap.get('basis')!r} invalid")
    if cap.get("basis") == "ac_managed_vendor" and cap.get("vendor_assumed_mow_freq") is None:
        WARNINGS.append(f"{mid}: acres-maintained figure with no assumed frequency — "
                        "cannot be normalized; request from vendor")

    hoc = m.get("cutting", {})
    lo, hi = hoc.get("hoc_min_in"), hoc.get("hoc_max_in")
    if lo is not None and hi is not None and lo > hi:
        ERRORS.append(f"{mid}: hoc_min_in {lo} > hoc_max_in {hi}")

    # a machine claiming fairway capability must be able to reach fairway HOC
    if m["capability"].get("fairways") == "capable" and lo is not None and lo > 0.75:
        ERRORS.append(f"{mid}: claims fairway capability but hoc_min_in={lo} is above fairway range")

    if prov.get("confidence") == "measured" and not any(
            "internal:trial" in (s.get("url") or "") for s in prov.get("sources") or []):
        WARNINGS.append(f"{mid}: confidence=measured but no internal trial source cited")


def main():
    files = [p for p in sorted(glob.glob("data/machines/*.yaml"))
             if not p.endswith("_TEMPLATE.yaml")]
    for p in files:
        check(p)
    print(f"checked {len(files)} machine records")
    for w in WARNINGS:
        print(f"  WARN  {w}")
    for e in ERRORS:
        print(f"  ERROR {e}")
    print(f"\n{len(ERRORS)} errors, {len(WARNINGS)} warnings")
    sys.exit(1 if ERRORS else 0)


if __name__ == "__main__":
    main()
