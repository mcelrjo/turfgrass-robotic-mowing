# Trial data

Three CSVs per session: `<session_id>_header.csv`, `_machine.csv`, `_operator.csv`.
Column definitions and activity types: `docs/TRIAL_PROTOCOL.md`.

**Labor is recorded once, on the operator log only.** `scripts/derive.py` reads labor
exclusively from the operator log; putting it in both places will not double the number,
it will just be ignored — but it will confuse the next person.

Round-one datasets (Ritz-Carlton Orlando, The Springs, Glenwild) need re-entry in this
structure before their coefficients can be regenerated automatically.
