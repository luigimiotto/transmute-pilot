# TransMuTe pilot web app

Read-only Streamlit interface for the pilot TSV dataset.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The app reads the UTF-8 TSV files in `data/`. Search matches English and Chinese text, romanization, glosses, contexts, and definitions. The concept view groups attestations through `concept_id`; the search view keeps individual source occurrences distinct.

## Publish

Push this folder to a GitHub repository, then deploy `app.py` through Streamlit Community Cloud. Keep the data in the public repo only if its transcription and image rights permit public redistribution. The current interface does not embed manuscript images.
