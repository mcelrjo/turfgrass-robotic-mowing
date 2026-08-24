# Trial Protocol v2

Supersedes the ad hoc sheets used in round one. Files: `data/trials/<session_id>_{header,machine,operator}.csv`.

## The four failures v2 exists to prevent

1. **Labor double-counting** between machine and operator logs.
   → Labor is recorded **once**, on the operator log only.
2. **Composite entries** ("mow + drive back + wash = 55 min") that cannot be decomposed.
   → One activity per row.
3. **Missing acreage** — two of three round-one courses reported none, forcing back-calculation.
   → Acres is a required header field.
4. **Unexplained gaps** — a 37-minute hole at one course; breaks folded into drive time.
   → Explicit `Non-productive` activity type. Record it. It is data, not failure.

## Observation bias

Operators work faster when watched. **Do not apply an assumed correction multiplier** — a
reviewer will attack an asserted haircut immediately, and rightly. Instead:

- Record whether the operator knew they were timed (`operator_aware_of_timing`).
- Where telematics exist (JDLink, MyTurf, Horizon), pull engine hours and ground speed for
  the observed day **and** matched unobserved days. That converts an assertion into a
  measurement with a confidence interval.
- Record breaks and gaps rather than absorbing them into task times.

Worth knowing: the round-one manual baselines already run *slower* than USGA published
figures, so the current manual data is not flattering to the robots.

## Activity types

**Machine log:** `Mow` · `Transit-transport` (operator drives) · `Transit-autonomous`
(self-drives) · `Setup` · `Task/retask` · `Return` · `Wash` · `Refuel/Recharge` ·
`Maintenance` · `Downtime-fault` · `Non-productive`

**Operator log:** `Mowing-attributable` · `Shepherding` · `Task switch loss` ·
`Alternate agronomy` · `Non-productive`

For `Alternate agronomy`, `would_have_been_done_anyway` is the critical field. Only work
marked `No` counts as captured work. Everything else was happening regardless and claiming
it would inflate the benefit.

## Priority gaps

1. **Rough mowing — manual and robotic.** Rough is the largest acreage on a course
   (~45 ac vs ~32 fairway) and has **zero** data. Highest-value trial to run next.
2. **Fully autonomous duty cycles.** Use the weekly duty-cycle log, not the session log.
   Do not force a continuously docked machine into a session structure.
3. **Quality of cut**, especially night vs. day and cool- vs. warm-season fairways under
   rotary mulching platforms. This resolves the ECHO classification dispute.
4. **Battery**: percent at session start and end, charge start and end clock times.
