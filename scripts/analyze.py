"""
Compute published results from data/trials/sessions.yaml.

Reports at three levels so sites of different sizes are comparable:

  1. AS MEASURED  - what was actually observed. Honest, but not comparable across sites,
                    because one site observed 32.7 acres and another 9.2.
  2. FULL COURSE  - each site's own measured rates applied to its full managed fairway area.
                    What that course actually gets.
  3. NORMALIZED   - every site's rates applied to a standard 18-hole course (31.9 fairway
                    acres, GCSAA). This is the level that puts all sites side by side.

The model separates fixed from variable labor, which is the key structural finding:

  autonomous labor = fixed per session + shepherding      <- a SESSION cost
  manual labor     = fixed per unit-session + rate x acres <- an ACRE cost

That asymmetry is why a site that mows more acres per session looks dramatically better:
autonomous fixed overhead amortizes over area, manual labor does not.

Writes data/reference/results.yaml. Do not edit that file by hand.
"""
import math
import os

import yaml

SESSIONS = "data/trials/sessions.yaml"
OUT = "data/reference/results.yaml"

REFERENCE_ACRES = 31.9      # GCSAA 18-hole fairway average
AUTO_SESSION_CAP = 16.5     # acres one autonomous unit covers per session (measured, site-01)
MANUAL_WINDOW_MIN = 240     # a 4-hour pre-play mowing window per operator
DEFAULT_MOW_FREQ = 3.0      # mowings per week; NOT reported by any site - see caveats
WAGE_DEFAULT = 24.50
DIESEL_DEFAULT = 4.50
ELEC_DEFAULT = 0.135
KWH_PER_AC = 2.7
FREQ_TABLE = [2.0, 3.0, 4.0, 5.0]


def decompose(site):
    """Split each run into fixed-per-session and variable-per-acre labor."""
    af = ash = mf = mv = ac = 0.0
    runs = site["runs"]
    for r in runs:
        a, m = r["auto"], r["manual"]
        ac += r["acres"]
        fixed = (a.get("setup") or 0) + (a.get("return") or 0) + (a.get("clean") or 0)
        if a.get("return") is None:
            # site-03 folded return and washdown into the final fairway entry
            fixed = (a.get("setup") or 0) + 20 + 3
        af += fixed
        ash += max((a.get("operator") or 0) - fixed, 0)
        u = m.get("units") or 1
        mf += ((m.get("setup") or 0) + (m.get("return") or 0) + (m.get("clean") or 0))
        mv += ((m.get("mow") or 0) + (m.get("transit") or 0)) * u
    n = len(runs)
    return {
        "auto_fixed_min_per_session": round(af / n, 1),
        "auto_shepherd_min_per_session": round(ash / n, 1),
        "manual_fixed_min_per_unit_session": round(mf / n, 1),
        "manual_variable_min_per_ac": round(mv / ac, 1),
    }


def model_pass(acres, c):
    """Operator minutes for one complete mowing pass of `acres`, both systems."""
    auto_sessions = math.ceil(acres / AUTO_SESSION_CAP)
    auto = auto_sessions * (c["auto_fixed_min_per_session"] + c["auto_shepherd_min_per_session"])
    ac_per_operator = MANUAL_WINDOW_MIN / c["manual_variable_min_per_ac"]
    unit_sessions = math.ceil(acres / ac_per_operator)
    manual = (unit_sessions * c["manual_fixed_min_per_unit_session"]
              + c["manual_variable_min_per_ac"] * acres)
    return {
        "acres": round(acres, 1),
        "auto_sessions": auto_sessions,
        "manual_unit_sessions": unit_sessions,
        "auto_min": round(auto),
        "manual_min": round(manual),
        "saved_min": round(manual - auto),
        "auto_hr": round(auto / 60, 1),
        "manual_hr": round(manual / 60, 1),
        "saved_hr": round((manual - auto) / 60, 1),
        "reduction_pct": round(100 * (manual - auto) / manual, 1),
    }


def weekly(p, freq):
    return {
        "mow_freq_per_week": freq,
        "manual_hr_per_week": round(p["manual_min"] * freq / 60, 1),
        "auto_hr_per_week": round(p["auto_min"] * freq / 60, 1),
        "saved_hr_per_week": round(p["saved_min"] * freq / 60, 1),
    }


def summarize(s):
    c = decompose(s)
    obs_ac = sum(r["acres"] for r in s["runs"])
    obs_fw = sum(r["fairways"] for r in s["runs"])
    holes = s["holes_managed_autonomous"]
    scale = holes / obs_fw
    full_ac = obs_ac * scale

    man_obs = sum((r["manual"].get("operator") or 0) for r in s["runs"])
    auto_obs = sum((r["auto"].get("operator") or 0) for r in s["runs"])
    fuel = sum((r["manual"].get("fuel_gal") or 0) for r in s["runs"])
    wage = s.get("wage_usd_hr") or WAGE_DEFAULT

    full = model_pass(full_ac, c)
    ref = model_pass(REFERENCE_ACRES, c)

    return {
        "code": s["code"],
        "facility_type": s["facility_type"],
        "region": s["region"],
        "turf": s["turf"],
        "sessions": s["sessions"],
        "holes_managed": holes,
        "coefficients": c,

        # level 1 - as measured
        "observed": {
            "acres": round(obs_ac, 1),
            "fairways": obs_fw,
            "acres_basis": s["acres_basis"],
            "manual_min": round(man_obs),
            "auto_min": round(auto_obs),
            "saved_min": round(man_obs - auto_obs),
            "saved_hr": round((man_obs - auto_obs) / 60, 1),
            "manual_min_per_ac": round(man_obs / obs_ac, 1),
            "auto_min_per_ac": round(auto_obs / obs_ac, 1),
            "reduction_pct": round(100 * (man_obs - auto_obs) / man_obs, 1),
        },

        # level 2 - the course's own full fairway area
        "full_course": {
            "acres": round(full_ac, 1),
            "scale_factor": round(scale, 2),
            "is_extrapolated": obs_fw < holes,
            **full,
            "weekly": [weekly(full, f) for f in FREQ_TABLE],
        },

        # level 3 - standard 18-hole reference course
        "normalized": {
            **ref,
            "weekly": [weekly(ref, f) for f in FREQ_TABLE],
        },

        "fuel_gal": round(fuel, 1) if fuel else None,
        "fuel_gal_per_ac": round(fuel / obs_ac, 2) if fuel else None,
        "wage_usd_hr": wage,
        "wage_is_reported": s.get("wage_usd_hr") is not None,
        "redeployed_log": s.get("redeployed_log", False),
        "redeployed_min": sum(t["minutes"] for t in s.get("redeployed", [])),
        "redeployed_tasks": s.get("redeployed", []),
        "note": s.get("note", ""),
    }


def main():
    data = yaml.safe_load(open(SESSIONS))
    sites = [summarize(s) for s in data["sites"]]
    n = len(sites)

    def mean(path):
        cur = [s for s in sites]
        for k in path:
            cur = [c[k] for c in cur]
        return round(sum(cur) / len(cur), 1)

    pooled_coef = {k: round(sum(s["coefficients"][k] for s in sites) / n, 1)
                   for k in sites[0]["coefficients"]}
    ref_pooled = model_pass(REFERENCE_ACRES, pooled_coef)

    obs_ac = sum(s["observed"]["acres"] for s in sites)
    obs_man = sum(s["observed"]["manual_min"] for s in sites)
    obs_auto = sum(s["observed"]["auto_min"] for s in sites)

    pooled = {
        "sites": n,
        "sessions": sum(s["sessions"] for s in sites),
        "observed_acres": round(obs_ac, 1),
        "observed_manual_hr": round(obs_man / 60, 1),
        "observed_auto_hr": round(obs_auto / 60, 1),
        "observed_saved_hr": round((obs_man - obs_auto) / 60, 1),
        "coefficients": pooled_coef,
        "reference_acres": REFERENCE_ACRES,
        "auto_session_cap_ac": AUTO_SESSION_CAP,
        "normalized": {**ref_pooled, "weekly": [weekly(ref_pooled, f) for f in FREQ_TABLE]},
        "normalized_saved_hr_per_week_range": [
            min(s["normalized"]["saved_hr"] * DEFAULT_MOW_FREQ for s in sites),
            max(s["normalized"]["saved_hr"] * DEFAULT_MOW_FREQ for s in sites),
        ],
        "reduction_pct_range": [min(s["normalized"]["reduction_pct"] for s in sites),
                                max(s["normalized"]["reduction_pct"] for s in sites)],
        "redeployed_hr": round(sum(s["redeployed_min"] for s in sites) / 60, 1),
        "redeployed_sites": sum(1 for s in sites if s["redeployed_log"]),
        "default_mow_freq": DEFAULT_MOW_FREQ,
    }
    pooled["normalized_saved_hr_per_week_range"] = [
        round(x, 1) for x in pooled["normalized_saved_hr_per_week_range"]]

    fuel_sites = [s for s in sites if s["fuel_gal"]]
    fuel_pa = (sum(s["fuel_gal"] for s in fuel_sites)
               / sum(s["observed"]["acres"] for s in fuel_sites)) if fuel_sites else 0
    econ = {
        "wage_default_usd_hr": WAGE_DEFAULT,
        "wage_reported_usd_hr": next((s["wage_usd_hr"] for s in sites if s["wage_is_reported"]), None),
        "diesel_usd_gal": DIESEL_DEFAULT,
        "electricity_usd_kwh": ELEC_DEFAULT,
        "kwh_per_ac_estimated": KWH_PER_AC,
        "fuel_gal_per_ac": round(fuel_pa, 2),
        "fuel_cost_per_ac": round(fuel_pa * DIESEL_DEFAULT, 2),
        "electric_cost_per_ac": round(KWH_PER_AC * ELEC_DEFAULT, 2),
        "energy_saved_per_ac": round(fuel_pa * DIESEL_DEFAULT - KWH_PER_AC * ELEC_DEFAULT, 2),
        "reference_weekly_value_default": round(
            ref_pooled["saved_min"] * DEFAULT_MOW_FREQ / 60 * WAGE_DEFAULT),
        "reference_annual_value_default": round(
            ref_pooled["saved_min"] * DEFAULT_MOW_FREQ / 60 * WAGE_DEFAULT * 30),
    }

    tasks = {}
    for s in sites:
        for t in s["redeployed_tasks"]:
            tasks[t["task"]] = tasks.get(t["task"], 0) + t["minutes"]
    task_list = [{"task": k, "minutes": v, "hours": round(v / 60, 1)}
                 for k, v in sorted(tasks.items(), key=lambda x: -x[1])]

    out = {
        "generated_by": "scripts/analyze.py",
        "warning": "GENERATED FILE - do not edit. Change data/trials/sessions.yaml and re-run.",
        "anonymization": data["meta"]["anonymization"],
        "method_note": (
            "Sites observed very different amounts of ground, so raw hours are not comparable. "
            "Each site's measured labor coefficients are therefore applied to a standard "
            f"{REFERENCE_ACRES}-acre 18-hole course. Autonomous labor is modelled as a per-session "
            "cost (setup, return, washdown, shepherding); manual labor as a per-acre cost. That "
            "asymmetry is the study's central structural finding."),
        "pooled": pooled,
        "economics": econ,
        "sites": sites,
        "redeployed_tasks": task_list,
        "caveats": [
            "Three sites and four sessions. Enough to show direction and magnitude, not enough "
            "for statistical inference. Treat every figure as preliminary.",
            "No site reported its fairway mowing frequency. Weekly figures use a stated frequency "
            "that the reader can change; frequency is now a required field for new sites.",
            "Two of three sites observed only part of their course. Their full-course figures are "
            "extrapolated from measured rates and assume unobserved fairways resemble observed ones.",
            "Manual and autonomous runs were recorded on different days, not simultaneously.",
            "Operators knew they were being timed. Observation bias would make manual mowing look "
            "faster than normal, which works against the autonomous case rather than for it.",
            "Only one site measured fairway acreage. The other two are estimated from the pooled "
            "autonomous mowing rate.",
            "Only one site reported a loaded wage. Dollar figures elsewhere use a national default.",
            "No site has reduced headcount or overtime. Labor savings are currently redeployed "
            "hours, not cash removed from a budget.",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        yaml.dump(out, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)

    c = pooled_coef
    print("Labor model (pooled across sites)")
    print(f"  autonomous = {c['auto_fixed_min_per_session']} min/session fixed "
          f"+ {c['auto_shepherd_min_per_session']} min shepherding")
    print(f"  manual     = {c['manual_fixed_min_per_unit_session']} min/unit-session fixed "
          f"+ {c['manual_variable_min_per_ac']} min/acre\n")
    print(f"Normalized to a {REFERENCE_ACRES}-acre 18-hole course, at {DEFAULT_MOW_FREQ} mowings/week:")
    print(f"  {'site':34s} {'manual':>9s} {'auto':>8s} {'SAVED':>9s} {'reduction':>10s}")
    for s in sites:
        w = [x for x in s["normalized"]["weekly"] if x["mow_freq_per_week"] == DEFAULT_MOW_FREQ][0]
        print(f"  {s['facility_type']+', '+s['region']:34s} {w['manual_hr_per_week']:8.1f}h "
              f"{w['auto_hr_per_week']:7.1f}h {w['saved_hr_per_week']:8.1f}h "
              f"{s['normalized']['reduction_pct']:9.1f}%")
    r = pooled["normalized_saved_hr_per_week_range"]
    print(f"\n  Across sites: {r[0]}-{r[1]} man-hours per week saved on a standard 18-hole course")
    print(f"  Worth ${econ['reference_weekly_value_default']:,}/week, "
          f"${econ['reference_annual_value_default']:,}/season at ${WAGE_DEFAULT}/hr over 30 weeks")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
