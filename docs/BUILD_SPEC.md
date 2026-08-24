# Turfgrass Robotic Mowing Decision Platform — Build Specification v0.1

**Status:** conceptual architecture. No code yet.
**Companion files:** `01_machine_registry.xlsx`, `02_course_intake.xlsx`, `03_trial_log_v2.xlsx`

---

## 1. What this platform is

An independent decision tool for turfgrass managers evaluating robotic mowing. Not a payback
calculator and not a vendor configurator. The question it answers is **not** "will this pay for
itself" but:

> *Given my acreage, fleet, labor situation and constraints — should I automate, what should I
> automate first, and how do I expand over time to maximize benefit?*

Three commitments define it and should not be negotiated away:

1. **Independence.** Vendor claims are labeled as vendor claims. Where independent trial data
   contradicts marketing, the tool says so.
2. **Tiered honesty.** Benefits are reported in tiers by certainty. Hard cash first, soft value
   last, native units never monetized. A model that can be argued down and still holds is
   stronger than one that can't be argued with.
3. **Time as the axis.** Nearly every benefit strengthens with time. A one-year payback figure
   hides the entire case; a ten-year cumulative view is where it lives.

Scope is golf first, all managed turf later. The architecture below is surface-agnostic so
sports fields, campuses, and sod production can be added without restructuring.

---

## 2. Architecture — five layers

```
┌─────────────────────────────────────────────────────────────┐
│ L5  PRESENTATION   scenarios side-by-side, 10-yr charts,     │
│                    pathway recommendation, risk register     │
├─────────────────────────────────────────────────────────────┤
│ L4  BENEFIT        portfolio with certainty weights,         │
│                    tiered reporting, native-unit outputs     │
├─────────────────────────────────────────────────────────────┤
│ L3  COST STACK     labor, energy, maintenance, capital,      │
│                    infrastructure, downtime                  │
├─────────────────────────────────────────────────────────────┤
│ L2  FLEET & SCHED  units required, sessions/day, charge      │
│                    cycles, surge coverage, failure matrix    │
├─────────────────────────────────────────────────────────────┤
│ L1  TIME ENGINE    two engines: SESSION and DUTY-CYCLE       │
└─────────────────────────────────────────────────────────────┘
          ▲                                    ▲
   Course Intake                       Machine Registry
   (user input)                        (coefficient library)
```

**Rule:** coefficients live in the registry, never in code. Every number in Layer 1–3 is
editable from the workbook without touching model logic. This is what lets the platform improve
as trial data arrives.

---

## 3. Layer 1 — two time engines, not one

This is the core intellectual point of the platform, and the thing every vendor comparison
currently gets wrong.

### 3a. Session engine — manual and semi-autonomous

```
T_labor = T_setup
        + T_transit_to_first
        + Σ (mow_time_i   × attendance_factor)
        + Σ (transit_j    × attendance_factor)
        + (shepherd_events × (direct_cost + switch_loss))
        + T_return + T_cleanup + T_recharge_or_refuel
```

| Parameter | Manual | Semi-auto, day (path-linked) | Semi-auto, night (LOS) |
|---|---|---|---|
| Attendance factor during mow | 1.00 | 0.00 | (1 − LOS productivity) |
| Attendance during transit | 1.00 | 0.00 if linked, 1.00 if not | 1.00 |
| Shepherd events | n/a | clusters − 1 | clusters − 1 |

**Attendance vs. co-location.** Path linking drives the *attendance* factor: is the operator
required to be present? Line-of-sight drives the *co-location* factor: is the operator's other
work constrained to the mower's vicinity? Both reduce to charged labor minutes, so the engine
stays simple, but they are different constraints and must be separately parameterized.

Charged night labor = `session_hours × (1 − LOS_productivity_factor)`. At 0.75–0.85 this lands
at 3.0–5.0 labor-min/ac — parity with day operation, against 32.6 for manual.

**LOS productivity is course-specific, not a fudge factor.** It equals the share of a course's
outstanding work that is hole-adjacent. Bunker-heavy courses with hand-watering score high;
courses whose backlog is shop and irrigation-system work score low. It is a survey field.

### 3b. Duty-cycle engine — fully autonomous

Docked units do not run sessions. They run continuous duty cycles.

```
units_required   = ceil(zone_acres / acres_maintained_per_unit)
labor_per_period = service_hours + intervention_hours   (NOT per mowing event)
energy_per_period= annual_kWh × (period / year)
```

**Never chart `ac/hr` against `acres maintained per unit`.** They are not the same quantity and
putting them on one axis is the single most common error in autonomous-mowing marketing.

---

## 4. Layer 2 — fleet and scheduling

**Semi-autonomous units required** = max of two constraints:

- *Window constraint:* `acres_per_event × machine_min_per_ac / available_window`
- *Cycle constraint:* session length + charge time. At 5.5 h session + 6 h charge = 11.5 h
  cycle, two cycles leaves no slack → **1.5 sessions/day is the planning figure, not 2.0.**

**Confirmed operating pattern** (all three trial courses): one semi-auto unit covers one nine
per working day; an 18-hole course runs a two-day rotation. Automation converts fairway mowing
from "whole course in one morning" to a rolling 2–3 day cycle — which has agronomic
consequences (uneven growth between nines, pattern rotation, tournament prep) that belong in
the tool as a stated trade-off, not a footnote.

**Surge capacity.** The retained conventional fleet covers days requiring a whole-course mow:
member-guest, tournament prep, post-rain catch-up, overseed transitions. Frame the robot as
**baseload** and the existing fleet as **surge and backup**. This explains fleet retention
without sounding like a concession.

**Failure coverage matrix.** For each scenario, report the share of routine load still met when
(a) the robot is down, (b) one conventional unit is down, (c) both. This is what makes the
single-point-of-failure risk concrete rather than rhetorical.

---

## 5. Layer 3 — cost stack

| Component | Notes |
|---|---|
| Labor | Loaded wage (gross + 25–35% burden). OT at 1.5×. Night shift premium if applicable. |
| Energy | Diesel gal/hr × $/gal vs. kWh/ac × $/kWh. Watch demand charges on fast charging. |
| Maintenance | Split by system: engine, hydraulic, reel/cutting, chassis, battery. Electric platforms eliminate the first two entirely — roughly 45% of non-reel service cost. |
| Capital | Purchase price, financing, useful life (hour-rated *and* calendar-capped), residual (default 0 — no secondary market data exists). |
| Infrastructure | Charging circuits, possible service upgrade, dock siting and power runs, boundary wire (ECHO TM-2000), shop space. **Routinely omitted from vendor ROI; must not be omitted here.** |
| Downtime | Faults per 100 machine-hours × mean repair time × consequence. |
| Retained-fleet carrying | ~$1,400/unit/yr insurance + minimum service. A mothballed mower is not free. |
| Training and setup | Boundary mapping, geofencing, staff training hours. |

---

## 6. Layer 4 — benefit portfolio

Four report tiers, decreasing certainty. Full definitions in the **Benefit Portfolio** sheet.

- **Tier 1 — Hard cash** (weight 0.80–0.95): fuel, oils and filters, reduced repairs.
- **Tier 2 — Converted cash** (0.30–0.70): overtime avoided, capital displacement, fleet life
  extension, hydraulic leak events, positions not backfilled.
- **Tier 3 — Realized value** (0.30–0.55, hours by default): work captured that wasn't getting
  done, playing window extended, surge capacity, task coverage reliability.
- **Tier 4 — Native units** (never monetized): presentation quality, CO₂, noise, spill risk.

**Design rules.**

1. The **Tier 1 floor must be stated first**. On a medium-tier course, fuel plus repairs alone
   (~$170k over ten years at ~0.9 confidence) covers the net capex of a one-unit, 50%-cut
   configuration several times over. Leading with the ~$838k gross gets the model dismissed.
2. **Tier 3 defaults to an hours ledger by task category**, not a dollar total. The list of what
   got done — bunker edging, hex-plugging Poa, pump station repair, moisture mapping — is more
   persuasive to a superintendent than a dollar figure and far less attackable.
3. **Confidence weights are user-adjustable.** A skeptical GM can zero out Tier 3 and still see
   the Tier 1 floor. That is a feature.
4. **Never monetize Tier 4.** The moment "better-looking fairways" carries a dollar sign, the
   whole model is discounted.

**Capital treatment — three modes**, because this is where the case actually turns:

| Mode | Description | Typical result |
|---|---|---|
| Additive | Buy robot, keep entire fleet | NPV-negative at most courses — **this is year one reality, show it** |
| Deferred replacement | Robot replaces the *next* purchase | Usually the strongest honest case |
| Trade now | Sell/trade a unit at residual | Weak — residual values are unknown |

The investment works not by retiring a machine today but by **not buying the next one**. So the
tool must know where a course sits in its replacement cycle. A club that just bought two new
fairway mowers has a materially worse case than one facing a replacement next spring — and that
has nothing to do with robot performance.

---

## 7. Layer 5 — outputs

**Required charts** (10-year horizon, escalated and discounted):

1. Cumulative savings by benefit tier — stacked area, one band per tier
2. Cumulative labor hours freed — stepped area, annotated at each FTE-equivalent threshold
3. CO₂ avoided — line, with the **location-specific** grid factor stated on the chart
4. Cash position by year including capex — the honest J-curve
5. Scenario comparison — all selected deployment tiers on one axis
6. Tornado sensitivity — wage, acreage, frequency, LOS factor, OT conversion, replacement year

**Required non-chart outputs:** the failure coverage matrix, the risk register filtered to the
selected configuration, the hours ledger by task category, and a recommended **adoption pathway**
(which tier first, what triggers moving to the next).

The pathway recommendation is the platform's differentiator. Nobody else answers "what first."

---

## 8. Platform coverage and the classification dispute

| Class | Platforms | Economic engine |
|---|---|---|
| Manual | Toro RM5510/5410, JD 7700A | Session |
| Semi-autonomous | FireFly AMP-L100, FireFly rough (TBD), Kress KR238/KR237E | Session |
| Fully autonomous | ECHO TM-2050, TM-2000, RP-1250 | Duty cycle |

**Open dispute requiring resolution before publication.** ECHO markets the TM-2050 as
maintaining "rough, semi-rough and fairways." Scott's published classification treats ECHO as
suitable only above ~1 inch HOC — i.e. not fairways or tees. A rotary floating-head mulcher
physically *fits* the height range but that is not the same as producing fairway quality of cut.

Until measured, the tool should display ECHO fairway capability as **vendor-claimed, not
independently verified**. The resolution is a measured trial scoring aftercut appearance,
scalping on contour, and clip dispersal at fairway HOC. Publishing that trial would establish
the platform's independence better than anything else it could do first.

---

## 9. Data gaps, ranked by how much they limit the model

| # | Gap | Consequence |
|---|---|---|
| 1 | **No rough mowing data at all** — manual or robotic | Rough is the largest acreage on a course (~45 ac vs ~32 fairway). Tiers 3–5 rest entirely on unverified coefficients. Highest-value gap to close. |
| 2 | FireFly rough mower unannounced; no public specs | Tier 4 and 5 cannot be modeled for FireFly |
| 3 | ECHO capacity claims range 5–18 ac/unit across sources | Unit count — and therefore capital — is unresolvable |
| 4 | Kress publishes duty cycle (20 ac / 48 hr), not a rate | Not comparable to session platforms without conversion |
| 5 | Battery pack kWh unknown, every platform | Energy cost and fleet sizing both rest on it |
| 6 | Fast-charge pricing and inclusion unknown | Charge time caps sessions/day, which caps surge capacity |
| 7 | No tee or approach trial data | Tier 5 partially unverified |
| 8 | No quality-of-cut measurements | Tier 4 has no evidence base |
| 9 | Maintenance intervals and costs, all platforms | Thinnest line in the cost stack |
| 10 | Continuous-mulch effect on N cycling and thatch | Agronomic unknown for full-auto |

---

## 10. Suggested next steps

1. **Close gap #1.** Run the v2 trial protocol on rough mowing at one course, manual and
   robotic. It is the largest acreage and has zero data.
2. **Resolve the ECHO classification** with a measured HOC-vs-quality trial. This establishes
   independence and is publishable in its own right.
3. **Send the Autonomous Registry sheet to all three vendors** as a fill-in request. The yellow
   cells are exactly what's missing; a vendor filling them is a low-friction ask.
4. **Re-run the three existing datasets through the v2 log structure** to eliminate the
   double-counting and confirm the derived coefficients hold under the cleaner definitions.
5. Only then build the engine. Coefficients first, code second.

---

## 11. Publication and credibility notes

- Every displayed coefficient should carry a provenance tag: *trial-derived*, *vendor-stated*,
  *published*, or *assumed*. Users can filter to trial-derived only.
- Where vendor claims and trial data disagree, show both. The Santaluz case study claims ~2,000
  hours saved annually and ~$115,000/yr — the hours figure reproduces closely under this model,
  but the dollar figure implies ~$57.50/hr, roughly double any loaded golf-maintenance wage.
  Showing that discrepancy transparently builds more trust than ignoring it.
- Observation bias in manual baselines should be **measured via telematics**, not asserted as a
  multiplier. Note that the three existing datasets already run *slower* than USGA published
  benchmarks, so the current manual baseline is not flattering to the robots — a good position
  to argue from.
