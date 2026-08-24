# Site Architecture

## The dual mission

Two audiences arrive with different questions, and the site must serve both without one
diluting the other:

| Audience | Question | Section |
|---|---|---|
| Researching a purchase | "What's out there? What are the real specs?" | **Specifications** |
| Evaluating a decision | "Does this work for *my* course?" | **Decision tool** |

The specification database is the traffic engine. People search "AMP-L100 vs KR238" long
before they search "autonomous mowing ROI." Specs bring them in; the decision tool is why
they stay and why they come back. Build specs first.

## Recommended stack

**Astro + YAML/CSV data + GitHub Pages.**

Why Astro over the alternatives:

- Ships zero JavaScript by default — spec pages are static HTML, fast and indexable. SEO is
  the whole game for the specification half of the site.
- Content collections read `data/*.yaml` at build time with schema validation. Your data
  files *are* the CMS; a grad student edits YAML, opens a PR, the site rebuilds.
- Islands architecture: the calculator is one React component on one page. Everything else
  stays static.
- Free static hosting on GitHub Pages. No server, no database, no running cost.

Not Next.js (heavier, server-oriented, more than this needs). Not Jekyll or Hugo (weak story
for an interactive calculator). Not a SPA (spec pages must be individually crawlable).

**Calculator runs entirely client-side.** No user data leaves the browser. Say so on the
page — superintendents are sharing budget and payroll figures, and a privacy guarantee you
can actually keep is worth more than an account system.

## Page inventory

```
/                             Landing: what this is, who maintains it, both entry points
/machines                     Filterable index — the SEO workhorse
/machines/[id]                One page per machine. Full specs, provenance, disputes
/compare?a=x&b=y              Side-by-side, shareable URL
/calculator                   The decision engine (React island)
/calculator/results/[hash]    Shareable results, state encoded in URL — no backend
/methodology                  How the model works. Full transparency.
/methodology/normalization    Why capacity figures aren't comparable and how we fix it
/methodology/coefficients     Every coefficient, its value, source, confidence
/data                         Download everything. CC BY 4.0.
/trials                       Published trial results
/glossary                     Semi- vs fully autonomous, attendance factor, managed acres
/contribute                   How to submit data
```

## Machine page — the template that matters

Every spec field renders with a **provenance chip**: `measured` / `published` / `vendor` /
`assumed`. Vendor claims are visibly marked as claims. Users can filter the whole site to
show measured data only.

Structure:
1. Identity — vendor, model, class, status
2. **Normalized capacity** — an interactive managed-acres figure that responds to a mowing
   frequency slider. This is the site's signature feature; nobody else publishes it.
3. Capability by surface, with conditional flags surfaced as toggles
4. Specifications, grouped, each with a provenance chip
5. **Disputes** — rendered prominently when `dispute: true`, showing both positions
6. Sources, with access dates
7. "What we still don't know" — the null fields, listed explicitly

That last section is unusual and it is the point. Publishing your gaps is what makes the
filled fields believable.

## The normalization widget

The single most valuable thing the site can offer. A superintendent seeing "ECHO TM-2050
maintains 12 acres" and "Kress KR238 does 20 acres in 48 hours" has no way to compare them.

The widget takes mowing frequency as input and returns managed acres for every machine on
one axis. Where a vendor figure can't be normalized (acres-maintained with no stated
frequency), the site shows **"cannot be normalized — awaiting vendor data"** rather than
guessing. That refusal is a credibility feature, not a gap.

## Editorial policy

1. No advertising, no sponsored placement, no affiliate links. State it on the About page.
2. Vendors may submit corrections through the same PR process as anyone else. Corrections
   are logged publicly.
3. Where trial data and vendor claims conflict, both are shown. Neither is deleted.
4. Funding sources disclosed on every page footer.

The project is being run with a vendor relationship. That is fine and normal — but it must
be disclosed prominently, and the editorial process must be visibly the same for FireFly as
for Kress and ECHO. The repository being public is the strongest evidence of that.

## Build order

**Phase 1 (weeks 1-4) — Specifications.** Machine index, machine pages, compare, glossary,
normalization widget. Ship it. It is useful on its own and starts accruing search traffic
while the model matures.

**Phase 2 (weeks 5-10) — Methodology.** Publish the model before the calculator. Invite
criticism while changes are still cheap.

**Phase 3 (weeks 11-16) — Calculator.** Intake wizard, scenario comparison, 10-year charts,
shareable results.

**Phase 4 — Trials and expansion.** Publish trial results as they complete. Add sports turf
and municipal surfaces once the golf model is stable.
