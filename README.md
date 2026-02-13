# UbiLife

<!-- shields placeholder -->
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

Analysis pipeline for the UbiLife mobile sensing dataset collected during UbiComp 2025 in Helsinki, Finland.

## Vision and Mission

- **Vision:** <!-- TODO: Add project vision -->
- **Mission:** <!-- TODO: Add project mission -->

## About

This project analyzes mobile sensing data from the UbiLife dataset collected during a week-long conference with ~82 participants (Oct 9-29, 2025). The dataset includes 15 data streams (location, step count, activity, surveys, weather, and more) with over 1 million records.

**Data types available:**
- Passive sensors: location, step count, activity recognition, ambient light, heart rate
- Active data: surveys (onboarding, daily stress/sleep, WHO-5, BFI-10, session ratings)
- Device data: battery state, device information, screen events
- Environmental: weather, air quality

## The Team

<!-- TODO: Add team members and roles -->

## Licensing

This project is licensed under the MIT License — see the [LICENSE.md](LICENSE.md) file for details.

## Citing

<!-- TODO: Add citation instructions -->

## Contact

<!-- TODO: Add contact details -->

---

## Repo Structure

```
├── LICENSE.md
├── README.md          <- The top-level README for users of this project.
├── CODE_OF_CONDUCT.md <- Guidelines for users and contributors of the project.
├── CONTRIBUTING.md    <- Information on how to contribute to the project.
├── pyproject.toml     <- Project dependencies and metadata.
├── data
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details.
│
├── models             <- Trained and serialized models, model predictions, or model summaries.
│
├── notebooks          <- Jupyter notebooks. The naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting.
│
├── project_management <- Meeting notes and other project planning resources.
│
├── src                <- Source code for use in this project.
│   │
│   ├── data           <- Scripts to download or generate data.
│   │
│   ├── models         <- Scripts to train models and then use trained models to make
│   │                     predictions.
│   │
│   └── visualisation  <- Scripts to create exploratory and results-oriented visualisations.
└──
```

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

Using uv (recommended):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

Using pip:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Data

Place the UbiLife dataset files in `data/raw/`. The raw data is not tracked in git due to its size (~587 MB).

To convert the raw JSON data to Parquet format for faster analysis, run the `convert_to_parquet()` function in the exploration notebook.
