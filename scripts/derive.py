"""
Recompute derived coefficients from raw trial CSVs.

Run in CI before every site build so published coefficients always trace to trial data.
Writes data/reference/derived.yaml — never edit that file by hand.
"""
import glob, os, sys
import yaml

try:
    import pandas as pd
except ImportError:
    print("pandas required: pip install -r requirements.txt"); sys.exit(1)

TRIALS = "data/trials"


def load_sessions():
    out = []
    for h in sorted(glob.glob(f"{TRIALS}/*_header.csv")):
        sid = os.path.basename(h).replace("_header.csv", "")
        m, o = f"{TRIALS}/{sid}_machine.csv", f"{TRIALS}/{sid}_operator.csv"
        if not (os.path.exists(m) and os.path.exists(o)):
            print(f"  skip {sid}: missing machine or operator log")
            continue
        out.append((sid, pd.read_csv(h), pd.read_csv(m), pd.read_csv(o)))
    return out


def derive(sid, hdr, mach, oper):
    acres = float(hdr["acres_mowed"].iloc[0])
    mow = mach.loc[mach.activity_type == "Mow", "duration_min"].sum()
    # labor comes from the operator log ONLY — never sum both logs
    lab = oper.loc[oper.attributable_to_mowing.astype(str).str.lower() == "yes",
                   "duration_min"].sum()
    shepherd = int((mach.activity_type == "Transit-transport").sum())
    alt = oper.loc[(oper.activity_type == "Alternate agronomy") &
                   (oper.would_have_been_done_anyway.astype(str).str.lower() == "no"),
                   "duration_min"].sum()
    nonprod = oper.loc[oper.activity_type == "Non-productive", "duration_min"].sum()
    total = oper["duration_min"].sum()
    return {
        "session_id": sid,
        "course": str(hdr["course"].iloc[0]),
        "surface": str(hdr["surface"].iloc[0]),
        "system_class": str(hdr["system_class"].iloc[0]),
        "acres": acres,
        "machine_min_per_ac": round(mow / acres, 2) if acres else None,
        "labor_min_per_ac": round(lab / acres, 2) if acres else None,
        "shepherd_events": shepherd,
        "captured_work_min": float(alt),
        "non_productive_share": round(nonprod / total, 3) if total else None,
    }


def main():
    sessions = load_sessions()
    if not sessions:
        print("no trial sessions found — nothing to derive")
        print("add CSVs to data/trials/ per docs/TRIAL_PROTOCOL.md")
        return
    rows = [derive(*s) for s in sessions]
    df = pd.DataFrame(rows)
    pooled = (df.groupby(["surface", "system_class"])
                .agg(sessions=("session_id", "count"),
                     acres=("acres", "sum"),
                     machine_min_per_ac=("machine_min_per_ac", "mean"),
                     labor_min_per_ac=("labor_min_per_ac", "mean"))
                .round(2).reset_index())
    out = {
        "generated_by": "scripts/derive.py",
        "warning": "GENERATED FILE — do not edit by hand. Edit data/trials/ and re-run.",
        "sessions": rows,
        "pooled": pooled.to_dict("records"),
    }
    with open("data/reference/derived.yaml", "w") as f:
        yaml.dump(out, f, sort_keys=False, default_flow_style=False)
    print(f"derived coefficients from {len(rows)} sessions")
    print(pooled.to_string(index=False))


if __name__ == "__main__":
    main()
