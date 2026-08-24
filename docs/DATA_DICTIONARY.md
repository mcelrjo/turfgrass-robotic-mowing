# Data Dictionary

## Confidence levels

| Level | Meaning | Rendered as |
|---|---|---|
| `measured` | From a controlled trial in `data/trials/` | Green chip |
| `published` | Peer-reviewed, government, or independent trade source | Blue chip |
| `vendor` | Manufacturer claim, not independently verified | Amber chip, labeled "vendor claim" |
| `assumed` | Project estimate; reasoning required in `notes` | Grey chip |

## Capability values

| Value | Meaning |
|---|---|
| `capable` | Verified by trial or uncontested engineering fact |
| `vendor_claimed` | Manufacturer says so; we have not verified |
| `conditional` | Capable only under stated conditions — see `capability.conditions` |
| `not_capable` | Cannot perform to acceptable standard |

`greens: not_capable` is enforced by the validator for every machine. No robotic option
exists at greens height of cut.

## Capacity basis — read this before adding a machine

Vendors publish capacity four incompatible ways. Record the **raw published figure and its
basis**. Never pre-convert; the normalizer does that.

| Basis | Meaning | Example |
|---|---|---|
| `ac_per_hr` | Throughput while actively mowing | FireFly 3.02 ac/hr |
| `ac_per_day` | Throughput per 24 h | Kress "20 ac / 48 hr" → 10 |
| `ac_per_week` | Throughput per 7 days | ECHO TM-850 "30,000 m²/week" → 7.41 |
| `ac_managed_vendor` | Area kept mowed at an **unstated** frequency | ECHO TM-2050 "maintains 12 ac" |

`ac_managed_vendor` **requires** `vendor_assumed_mow_freq`. Without it the figure cannot be
normalized and the site displays it as unnormalizable. Do not invent a frequency to make the
number work — the missing frequency is itself the finding.

## Managed acres — the universal metric

```
weekly_throughput = daily_capacity × working_days_per_week
managed_acres     = weekly_throughput ÷ mow_frequency_per_week
```

Validated against Ritz-Carlton: 16.5 ac/day, 7 working days, each nine mowed every other
day (3.5×/wk) → **33.0 managed acres**. Actual fairway acreage: **32.7 ac**.

Mowing frequency is a **divisor**, so it is never optional. Doubling frequency halves the
acres one unit can manage. The site must show this, because it is the most common error in
autonomous-mowing purchase decisions.

## Economic engine

| Engine | Applies to | Labor model |
|---|---|---|
| `session` | Manual, semi-autonomous | Per mowing event: setup, transport, task, return, wash |
| `duty_cycle` | Fully autonomous | Per period: service and intervention hours only |

Enforced: `fully_autonomous` → `duty_cycle`; `manual` → `session`.
