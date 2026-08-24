# Data Requests

Hand these to a research assistant. No git or programming needed — each produces a filled
spreadsheet or a set of CSVs that gets imported into the repository.

Every request follows the same rule: **a value with no source doesn't get used.** Record where
each number came from and when it was accessed. "The dealer said so" is a source — write it
down that way. A guess is not, and an empty cell is far more useful than an invented number.

---

## Request 1 — Fill the machine specification gaps

**Deliverable:** `intake/01_machine_registry.xlsx`, yellow cells completed.

Every yellow cell is a spec no public source has published. For each machine, work through:
manufacturer spec sheet, dealer quote, operator's manual, then a direct email to the
manufacturer.

Highest value, in order:
1. **Battery pack capacity (kWh)** for every electric platform. Unpublished across the entire
   industry. It drives both energy cost and fleet sizing.
2. **Charge rate and fast-charge availability and price.** Charge time caps how many sessions a
   machine can run per day, which caps everything downstream.
3. **List price in USD** for the Kress and ECHO units. Kress publishes GBP including VAT;
   convert and add US dealer margin, and record both figures.
4. **Service intervals and annual maintenance cost** for every machine, manual included.

## Request 2 — Resolve the capacity-basis problem

**Deliverable:** a short memo plus updated workbook rows.

Three machines publish capacity as "maintains up to N acres" without stating a mowing
frequency. Without the frequency the number has no fixed meaning, so the site currently shows
them as unnormalizable.

Email each manufacturer and ask one question: *at what mowing frequency does your published
acreage figure assume the machine operates?*

Note the precedent: ECHO publishes the TM-850 as 30,000 m² **per week**, which is an explicit
throughput basis. If they restated every model that way the problem disappears — worth saying
so in the email.

## Request 3 — Re-enter the three existing trial datasets

**Deliverable:** CSVs in `data/trials/`, using `intake/03_trial_log_v2.xlsx` as the structure.

The original Ritz-Carlton, Springs and Glenwild sheets have four known problems: labor
double-counted between logs, composite entries that can't be decomposed, missing acreage, and
unexplained time gaps. Re-entering them in the v2 structure lets coefficients regenerate
automatically instead of being computed by hand.

Rules: labor is recorded **once**, on the operator log only. One activity per row. Non-productive
time gets its own rows — record it honestly, it's data.

## Request 4 — Collect rough mowing data

**Deliverable:** new trial sessions using `intake/03_trial_log_v2.xlsx`.

**This is the biggest gap in the entire project.** Rough is roughly 45 acres on a typical
course against 32 for fairways, and there is currently zero data on it — manual or robotic.
Every conclusion about rough automation rests on assumptions.

Needed: manual rough mowing time-motion at one course, then robotic if a unit is available.

## Request 5 — Quality of cut assessment

**Deliverable:** the Quality Assessment sheet in `intake/03_trial_log_v2.xlsx`, plus photos.

Two questions worth publishing on:
1. **Night vs. day cut quality.** RTK holds a line without visual reference to the previous
   pass; a human at 2 a.m. cannot. This is the one benefit with no manual equivalent at any
   wage, and it needs measurement rather than assertion.
2. **Rotary mulching platforms at fairway height, cool-season vs. warm-season.** ECHO markets
   the TM-2050 for fairways without qualification. The project position is that it holds
   acceptable quality on cool-season turf only. Resolving this with measured data would
   establish the site's independence better than anything else it could publish.

Score on the 1–9 NTEP scale: aftercut appearance, line straightness, stripe consistency,
clean-up passes, scalp events, clip clumping.

## Request 6 — Course profiles

**Deliverable:** `intake/02_course_intake.xlsx`, one per participating course.

Acreage by surface is the required field — two of the three original courses reported none,
which forced everything to be back-calculated from a single anchor. The other fields that
change conclusions most: overtime hours, season length, and where each course sits in its
equipment replacement cycle.
