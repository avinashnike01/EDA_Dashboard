# EDA Dashboard

A Streamlit app for exploratory data analysis. You upload a file and explore it with PyGWalker, D-Tale, Mito, Plotly charts and a ydata-profiling report, behind a simple login (streamlit-authenticator).

This was a personal side project and isn't actively maintained.

## Setup

Python 3.10 or 3.11 is recommended (ydata-profiling had trouble on 3.12 when this was written).

```
pip install -r requirements.txt
cp st_auth/config.example.yaml st_auth/config.yaml
```

Then edit `st_auth/config.yaml`:

- put a bcrypt hash in each `password` field, not the plain password (streamlit-authenticator's `Hasher` can generate one)
- set `cookie.key` to a long random string

Run it with:

```
streamlit run main.py
```

## Notes

`st_auth/config.yaml`, `.env`, `.streamlit/secrets.toml`, the `viz_config/*.json` chart specs and any data files are gitignored on purpose. Keep credentials and data out of the repo.
