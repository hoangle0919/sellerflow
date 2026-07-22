# Validation datasets — sources

Real, public credit datasets used by `../validate_on_real_data.py` to validate
the RBF modeling methodology on real borrowers with real default outcomes.
Both are open, widely-cited academic benchmarks, bundled here for one-command
reproducibility.

- **`german.data-numeric`** — UCI Statlog (German Credit Data). 1,000 real loan
  applicants labelled good/bad credit. 24 numeric attributes.
  Source: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data

- **`taiwan.csv`** — UCI "Default of Credit Card Clients" (Taiwan, 2005). 30,000
  real credit-card accounts labelled by default-payment-next-month. Converted
  from the original `.xls` to CSV, unmodified otherwise.
  Source: https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
  Yeh, I. C., & Lien, C. H. (2009), *Expert Systems with Applications*.

These validate the *method*, not RBF's production merchant model (different
features; no real merchant outcomes yet). See `../validate_on_real_data.py`.
