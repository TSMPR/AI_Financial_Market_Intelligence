# Contributing

1. Fork the repository and create a focused feature branch.
2. Create a virtual environment and install `pip install -r requirements.txt`.
3. Run `pytest -q` before submitting changes.
4. Keep data-provider access isolated in `services/`; never commit credentials.
5. Document financial assumptions, edge cases and data provenance.
6. Add tests for calculations and failure paths. Avoid look-ahead bias in any
   future predictive feature.

Please do not submit investment claims unsupported by reproducible evidence.
