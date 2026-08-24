# Changelog

Coefficient sets are versioned so published results stay reproducible.

## [0.1.0] — 2026-08-24
Initial public release.

- 10 machine records: FireFly AMP-L100 and AMP rough (placeholder); ECHO TM-2050, TM-850,
  TM-2000; Kress KR238, KR237E; Toro Reelmaster 5510-D and 5410-D; John Deere 7700A
- Capacity normalization to managed acres, validated against measured course data
  (16.5 ac/day × 7 working days ÷ 3.5 mows per week = 33.0 ac against 32.7 ac actual)
- Coefficient library v0.1.0 derived from three field trials
- Astro site: machine index, spec pages, methodology, normalization slider
- Data validation and deploy in one GitHub Actions workflow
- Blank intake workbooks under `intake/` for data collection
