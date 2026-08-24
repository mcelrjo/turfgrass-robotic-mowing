"""
Compute the published survey results from data/trials/sessions.yaml.

Writes data/reference/results.yaml, which the site reads directly. Never edit that file
by hand — change the session data and re-run this.

    python scripts/analyze.py
"""
import os
import yaml

SESSIONS = "data/trials/sessions.yaml"
OUT = "data/reference/results.yaml"

WAGE_DEFAULT = 24.50      # BLS grounds-maintenance median + 33% burden
DIESEL_DEFAULT = 4.50     # USD/gal, off-road
ELEC_DEFAULT = 0.135      # USD/kWh, US commercial average
KWH_PER_AC = 2.7          # estimated; battery pack capacity still unpublished


def summarize_site(s):
    ac = man_lab = auto_lab = man_mow = auto_mow = auto_transit = man_transit = 0.0
    man_machine_min = fuel = 0.0
    for r in s["runs"]:
        a, m = r["auto"], r["manual"]
        ac += r["acres"]
        auto_lab += a.get("operator") or 0
        man_lab += m.get("operator") or 0
        auto_mow += a.get("mow") or 0
        man_mow += m.get("mow") or 0
        auto_transit += a.get("transit") or 0
        man_transit += m.get("transit") or 0
        man_machine_min += (m.get("mow") or 0) * (m.get("units") or 1)
        fuel += m.get("fuel_gal") or 0

    wage = s.get("wage_usd_hr") or WAGE_DEFAULT
    saved_min = man_lab - auto_lab
    return {
        "code": s["code"],
        "facility_type": s["facility_type"],
        "region": s["region"],
        "turf": s["turf"],
        "sessions": s["sessions"],
        "acres_observed": round(ac, 1),
        "acres_basis": s["acres_basis"],
        "manual_labor_min": round(man_lab),
        "auto_labor_min": round(auto_lab),
        "labor_saved_min": round(saved_min),
        "labor_saved_hr": round(saved_min / 60, 1),
        "labor_reduction_pct": round(100 * saved_min / man_lab, 1) if man_lab else None,
        "manual_labor_min_per_ac": round(man_lab / ac, 1),
        "auto_labor_min_per_ac": round(auto_lab / ac, 1),
        "auto_machine_min_per_ac": round(auto_mow / ac, 1),
        "manual_machine_min_per_ac": round(man_machine_min / ac, 1),
        "auto_transit_min": round(auto_transit),
        "manual_transit_min": round(man_transit),
        "fuel_gal": round(fuel, 1) if fuel else None,
        "fuel_gal_per_ac": round(fuel / ac, 2) if fuel else None,
        "wage_usd_hr": wage,
        "wage_is_reported": s.get("wage_usd_hr") is not None,
        "value_saved_usd": round(saved_min / 60 * wage),
        "value_saved_usd_per_ac": round(saved_min / 60 * wage / ac, 2),
        "redeployed_log": s.get("redeployed_log", False),
        "redeployed_min": sum(t["minutes"] for t in s.get("redeployed", [])),
        "redeployed_tasks": s.get("redeployed", []),
        "note": s.get("note", ""),
    }


def main():
    data = yaml.safe_load(open(SESSIONS))
    sites = [summarize_site(s) for s in data["sites"]]

    ac = sum(s["acres_observed"] for s in sites)
    man = sum(s["manual_labor_min"] for s in sites)
    aut = sum(s["auto_labor_min"] for s in sites)
    redeployed = sum(s["redeployed_min"] for s in sites)
    logged_redeploy = [s for s in sites if s["redeployed_log"]]
    fuel_sites = [s for s in sites if s["fuel_gal"]]

    pooled = {
        "sites": len(sites),
        "sessions": sum(s["sessions"] for s in sites),
        "acres_observed": round(ac, 1),
        "manual_labor_hr": round(man / 60, 1),
        "auto_labor_hr": round(aut / 60, 1),
        "labor_saved_hr": round((man - aut) / 60, 1),
        "labor_reduction_pct": round(100 * (man - aut) / man, 1),
        "manual_labor_min_per_ac": round(man / ac, 1),
        "auto_labor_min_per_ac": round(aut / ac, 1),
        "labor_saved_min_per_ac": round((man - aut) / ac, 1),
        "auto_machine_min_per_ac": round(
            sum(s["auto_machine_min_per_ac"] * s["acres_observed"] for s in sites) / ac, 1),
        "manual_machine_min_per_ac": round(
            sum(s["manual_machine_min_per_ac"] * s["acres_observed"] for s in sites) / ac, 1),
        "redeployed_hr": round(redeployed / 60, 1),
        "redeployed_sites": len(logged_redeploy),
        "fuel_gal_per_ac": round(
            sum(s["fuel_gal"] for s in fuel_sites)
            / sum(s["acres_observed"] for s in fuel_sites), 2) if fuel_sites else None,
    }

    # what a saved hour is worth, and what it costs to run, at pooled rates
    per_ac_saved_hr = pooled["labor_saved_min_per_ac"] / 60
    econ = {
        "wage_default_usd_hr": WAGE_DEFAULT,
        "wage_reported_usd_hr": next((s["wage_usd_hr"] for s in sites if s["wage_is_reported"]), None),
        "labor_value_per_ac_at_default": round(per_ac_saved_hr * WAGE_DEFAULT, 2),
        "diesel_usd_gal": DIESEL_DEFAULT,
        "electricity_usd_kwh": ELEC_DEFAULT,
        "kwh_per_ac_estimated": KWH_PER_AC,
        "fuel_cost_per_ac": round((pooled["fuel_gal_per_ac"] or 0) * DIESEL_DEFAULT, 2),
        "electric_cost_per_ac": round(KWH_PER_AC * ELEC_DEFAULT, 2),
        "energy_saved_per_ac": round((pooled["fuel_gal_per_ac"] or 0) * DIESEL_DEFAULT
                                     - KWH_PER_AC * ELEC_DEFAULT, 2),
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
        "pooled": pooled,
        "economics": econ,
        "sites": sites,
        "redeployed_tasks": task_list,
        "caveats": [
            "Three sites and four sessions. Enough to show direction and magnitude, not enough "
            "for statistical inference. Treat every figure as preliminary.",
            "Manual and autonomous runs were recorded on different days, not simultaneously.",
            "Operators knew they were being timed. Observation bias would make manual mowing look "
            "faster than normal, which works against the autonomous case rather than for it.",
            "Only one site measured fairway acreage. The other two are estimated from the pooled "
            "autonomous mowing rate.",
            "Only one site reported a loaded wage. Dollar figures at other sites use a national "
            "default and are labelled as such.",
            "No site has reduced headcount or overtime. Labor savings are currently redeployed "
            "hours, not cash removed from a budget.",
            "Two of three sites logged what the freed operator actually did. The third did not.",
        ],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        yaml.dump(out, f, sort_keys=False, default_flow_style=False, allow_unicode=True, width=100)

    p = pooled
    print(f"{p['sites']} sites, {p['sessions']} sessions, {p['acres_observed']} acres observed")
    print(f"  manual  {p['manual_labor_hr']:6.1f} labor-hr   ({p['manual_labor_min_per_ac']} min/ac)")
    print(f"  auto    {p['auto_labor_hr']:6.1f} labor-hr   ({p['auto_labor_min_per_ac']} min/ac)")
    print(f"  saved   {p['labor_saved_hr']:6.1f} labor-hr   ({p['labor_reduction_pct']}% reduction)")
    print(f"  redeployed and logged: {p['redeployed_hr']} hr at {p['redeployed_sites']} of {p['sites']} sites")
    print(f"\n  {'site':9s} {'type':14s} {'ac':>6s} {'man/ac':>7s} {'auto/ac':>8s} {'saved hr':>9s} {'reduction':>10s}")
    for s in sites:
        print(f"  {s['code']:9s} {s['facility_type']:14s} {s['acres_observed']:6.1f} "
              f"{s['manual_labor_min_per_ac']:7.1f} {s['auto_labor_min_per_ac']:8.1f} "
              f"{s['labor_saved_hr']:9.1f} {s['labor_reduction_pct']:9.1f}%")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
