"""
Capacity normalization — the one function that makes every platform comparable.

Vendors publish capacity on at least four incompatible bases:
  ac_per_hr          FireFly (session throughput while running)
  ac_per_day         Kress   ("20 acres in 48 hours" -> 10 ac/day)
  ac_per_week        ECHO TM-850 ("30,000 m2/week" -> 7.41 ac/wk)
  ac_managed_vendor  ECHO TM-2050 ("maintains up to 12 acres") — at an UNSTATED frequency

Everything reduces to MANAGED ACRES: the area one unit can keep mowed at the user's
frequency. That is the number a superintendent actually needs.

    weekly_throughput = daily_capacity * working_days_per_week
    managed_acres     = weekly_throughput / mow_frequency_per_week

Validated against Ritz-Carlton: 16.5 ac/day, 7 working days, each nine mowed every other
day (3.5x/wk) -> 33.0 managed acres. Actual fairway acreage: 32.7. Match.
"""

import yaml


class UnnormalizableCapacity(Exception):
    """Raised when a vendor 'acres maintained' figure has no stated frequency."""


def daily_capacity_ac(machine, session_hours=5.5):
    """Reduce any published basis to acres per day."""
    cap = machine["capacity"]
    basis, value = cap["basis"], cap["value"]
    if value is None:
        return None
    if basis == "ac_per_hr":
        return value * session_hours
    if basis == "ac_per_day":
        return value
    if basis == "ac_per_week":
        return value / 7.0            # duty-cycle machines run every day
    if basis == "ac_managed_vendor":
        freq = cap.get("vendor_assumed_mow_freq")
        if freq is None:
            raise UnnormalizableCapacity(
                f"{machine['id']}: capacity given as acres maintained ({value} ac) with no "
                "vendor_assumed_mow_freq. Cannot normalize. Request the assumed mowing "
                "frequency from the vendor."
            )
        return value * freq / 7.0
    raise ValueError(f"unknown capacity basis: {basis}")


def managed_acres(machine, mow_freq_per_week, working_days_per_week=None, session_hours=5.5):
    """Acres one unit can keep mowed at the user's frequency."""
    if working_days_per_week is None:
        # duty-cycle machines are docked and run every day; session machines follow the crew
        working_days_per_week = 7 if machine["economic_engine"] == "duty_cycle" else 5
    daily = daily_capacity_ac(machine, session_hours)
    if daily is None or not mow_freq_per_week:
        return None
    return daily * working_days_per_week / mow_freq_per_week


def units_required(machine, zone_acres, mow_freq_per_week, **kw):
    import math
    m = managed_acres(machine, mow_freq_per_week, **kw)
    if not m:
        return None
    return math.ceil(zone_acres / m)


if __name__ == "__main__":
    import sys, glob
    print(f"{'machine':28s} {'basis':20s} {'ac/day':>7s} " +
          "  managed ac @ 2x / 3x / 3.5x / 5x per week")
    for path in sorted(glob.glob("data/machines/*.yaml")):
        if path.endswith("_TEMPLATE.yaml"):
            continue
        m = yaml.safe_load(open(path))
        try:
            d = daily_capacity_ac(m)
            vals = "  ".join(
                f"{(managed_acres(m, f) or 0):6.1f}" for f in (2, 3, 3.5, 5))
            print(f"{m['id']:28s} {m['capacity']['basis']:20s} "
                  f"{(d or 0):7.2f}   {vals}")
        except UnnormalizableCapacity as e:
            print(f"{m['id']:28s} {m['capacity']['basis']:20s} " + "BLOCKED — " + str(e).split(": ",1)[1][:60])
