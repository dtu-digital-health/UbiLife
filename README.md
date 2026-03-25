# UbiLife

<!-- shields placeholder -->
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

Analysis pipeline for the UbiLife mobile sensing dataset collected during UbiComp 2025 in Helsinki, Finland.

## About

This project analyzes mobile sensing data from the UbiLife dataset collected during a week-long conference with ~82 participants (Oct 9-29, 2025). The dataset includes 15 data streams (location, step count, activity, surveys, weather, and more) with over 1 million records.

**Data types available:**
- Passive sensors: location, step count, activity recognition, ambient light, heart rate
- Active data: surveys (onboarding, daily stress/sleep, WHO-5, BFI-10, session ratings)
- Device data: battery state, device information, screen events
- Environmental: weather, air quality

## Licensing

This project is licensed under the MIT License — see the [LICENSE.md](LICENSE.md) file for details.

---

## Repo Structure

```
├── LICENSE.md
├── README.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── pyproject.toml        <- Project dependencies and metadata.
├── data
│   ├── processed         <- Processed parquet files (tracked in git).
│   └── raw               <- The original, immutable data dump (not tracked).
│
├── notebooks             <- Jupyter notebooks for exploration and data preparation.
│
├── reports               <- Generated analysis as LaTeX, presentations, etc.
│   └── figures           <- Generated graphics and figures.
│
└── src                   <- Source code for use in this project.
    ├── data              <- Data parsing and transformation scripts.
    └── visualisation     <- Plotting and visualisation utilities.
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