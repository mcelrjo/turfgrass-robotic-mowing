# Turfgrass Robotic Mowing — Specifications & Decision Platform

An independent reference for turfgrass managers evaluating robotic mowing.

1. **Specification database** — vendor-neutral, normalized specs for autonomous and
   conventional turf mowers, with a source on every value.
2. **Decision engine** — enter your acreage, fleet and labor; get a manual-vs-robotic
   comparison across deployment levels over a 10-year horizon. *(in development)*

Maintained by the Auburn University turfgrass program.
Live site: `https://<your-username>.github.io/<repo-name>/`

---

## How to work on this

One person maintains the repository. Everything happens on `main`.

```powershell
git pull                              # start of session
# ...edit files under data/ ...
python scripts/validate.py            # catch mistakes before pushing
git add -A
git commit -m "Add Kress KR174 record"
git push                              # site rebuilds and redeploys, ~2 minutes
```

That is the whole workflow. No branches, no pull requests.

If `validate.py` reports errors, fix them before pushing — the deploy will fail otherwise and
the live site will keep serving the previous version until it passes.

## Layout

```
data/                 the single source of truth
  trials/sessions.yaml  ← the survey dataset the site is built on
  machines/           one YAML file per machine model
  courses/            course profiles from field trials
  trials/             time-motion trial data (CSV)
  reference/          coefficients, capability conditions
scripts/              validate, normalize, derive, import
site/                 Astro site; builds from data/ at compile time
docs/                 methodology, protocols, data dictionary
intake/               blank workbooks to hand out for data collection
```

**Golden rule:** no number is hardcoded in site code. Every coefficient lives in
`data/reference/coefficients.yaml` with a source. If it can't be cited, it doesn't ship.

## Local preview

```powershell
cd site
npm install          # first time only
npm run dev          # http://localhost:4321, hot-reloads as you edit data
```

Requires Node 20+ (`winget install OpenJS.NodeJS.LTS`).

## Adding data from a research assistant

Assistants don't need git access. They fill in a workbook from `intake/`, send it back, and
you convert it:

```powershell
python scripts/import_from_xlsx.py path\to\filled_registry.xlsx
python scripts/validate.py
git add -A && git commit -m "Import machine specs from RA" && git push
```

See `docs/DATA_REQUESTS.md` for the assignments to hand out.

## Useful commands

| Command | Does |
|---|---|
| `python scripts/validate.py` | Checks every data file. Run before each push. |
| `python scripts/normalize.py` | Prints the managed-acres table for all machines |
| `python scripts/analyze.py` | Recomputes the published survey results from session data |
| `python scripts/derive.py` | Recomputes coefficients from trial CSVs |
| `python scripts/import_from_xlsx.py <file>` | Converts a filled workbook into YAML records |

## License

Code MIT. Data and documentation CC BY 4.0.
