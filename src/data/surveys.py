"""Parse survey.parquet into clean per-type DataFrames."""

from pathlib import Path

import numpy as np
import pandas as pd


# ── Helpers ──────────────────────────────────────────────────────────────────


def _col(step_id: str) -> str:
    """Build the full parquet column name for a survey answer step."""
    return f"measurement.data.result.results.{step_id}.results.answer"


def _extract_choice(raw):
    """Extract (value, text) from an RPChoice answer (ndarray / scalar / NaN)."""
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return None, None
    if isinstance(raw, np.ndarray):
        raw = raw.tolist()
    if isinstance(raw, list) and raw and isinstance(raw[0], dict):
        if len(raw) == 1:
            return raw[0].get("value"), raw[0].get("text")
        return ([c.get("value") for c in raw],
                [c.get("text") for c in raw])
    return raw, str(raw)


def _value(series: pd.Series) -> pd.Series:
    """Extract numeric value from an RPChoice column."""
    return series.apply(lambda x: _extract_choice(x)[0])


def _text(series: pd.Series) -> pd.Series:
    """Extract text from an RPChoice column, joining multi-select."""
    def _get(x):
        _, t = _extract_choice(x)
        return ", ".join(str(s) for s in t) if isinstance(t, list) else t
    return series.apply(_get)


# ── Public API ───────────────────────────────────────────────────────────────


def load_submitted(parquet_dir: Path) -> pd.DataFrame:
    """Load survey.parquet, keep submitted only, add timestamp + participant_id."""
    df = pd.read_parquet(parquet_dir / "survey.parquet")
    df = df[df["measurement.data.status"] == "submitted"].copy()
    df["timestamp"] = pd.to_datetime(
        df["measurement.sensorStartTime"], unit="us", errors="coerce"
    )
    df["date"] = df["timestamp"].dt.date
    df["participant_id"] = df["dataStream.studyDeploymentId"]
    df["survey_type"] = df["measurement.data.result.identifier"]
    return df


def parse_daily_stress(sub: pd.DataFrame) -> pd.DataFrame:
    """One row per participant per day: stress level (0-10)."""
    col = _col("daily.stress.step")
    rows = sub[sub["survey_type"] == "daily.stress.task"].dropna(subset=[col])
    return rows[["participant_id", "date", "timestamp"]].assign(
        stress_level=rows[col].astype(float),
    )


def parse_daily_sleep(sub: pd.DataFrame) -> pd.DataFrame:
    """One row per participant per day: sleep quality + hours."""
    col_q, col_h = _col("daily.sleep.step"), _col("daily.sleep.hours.step")
    rows = sub[sub["survey_type"] == "daily.sleep.task"]
    rows = rows[rows[col_q].notna() | rows[col_h].notna()]
    return rows[["participant_id", "date", "timestamp"]].assign(
        sleep_quality_value=_value(rows[col_q]),
        sleep_quality_text=_text(rows[col_q]),
        sleep_hours_value=_value(rows[col_h]),
        sleep_hours_text=_text(rows[col_h]),
    )


def parse_onboarding(sub: pd.DataFrame) -> pd.DataFrame:
    """One row per participant: demographics + conference background."""
    rows = sub[sub["survey_type"] == "onboarding.task"]
    steps = {k: _col(f"onboarding.{k}.step") for k in
             ["age", "gender", "academic", "prior", "presenter"]}

    df = rows[["participant_id", "timestamp"]].copy()
    df["age"] = pd.to_numeric(rows[steps["age"]], errors="coerce")
    for field in ("gender", "academic", "prior"):
        df[f"{field}_value"] = _value(rows[steps[field]])
        df[f"{field}_text"] = _text(rows[steps[field]])
    df["presenter_texts"] = _text(rows[steps["presenter"]])
    return df.sort_values("timestamp").drop_duplicates("participant_id", keep="first")


def parse_who5(sub: pd.DataFrame) -> pd.DataFrame:
    """One row per participant: WHO-5 wellbeing index."""
    rows = sub[sub["survey_type"] == "who5.task"].copy()
    for q in range(1, 6):
        rows[f"q{q}"] = pd.to_numeric(
            _value(rows[_col(f"survey.who5.question.{q}")]), errors="coerce"
        )
    rows = rows.dropna(subset=[f"q{q}" for q in range(1, 6)])
    for q in range(1, 6):
        rows[f"q{q}"] = rows[f"q{q}"].astype(int)

    df = rows[["participant_id", "timestamp", "q1", "q2", "q3", "q4", "q5"]].copy()
    df["raw_sum"] = df[["q1", "q2", "q3", "q4", "q5"]].sum(axis=1)
    df["pct_score"] = df["raw_sum"] * 4
    return df.sort_values("timestamp").drop_duplicates("participant_id", keep="first")


def parse_bfi10(sub: pd.DataFrame) -> pd.DataFrame:
    """One row per participant: BFI-10 Big Five personality dimensions."""
    rows = sub[sub["survey_type"] == "bfi10.task"].copy()
    for q in range(1, 11):
        rows[f"i{q}"] = pd.to_numeric(
            _value(rows[_col(f"bfi10.question{q}")]), errors="coerce"
        )
    rows = rows.dropna(subset=[f"i{q}" for q in range(1, 11)])

    df = rows[["participant_id", "timestamp"]].copy()
    df["extraversion"] = (4 - rows["i1"] + rows["i6"]) / 2
    df["agreeableness"] = (rows["i2"] + 4 - rows["i7"]) / 2
    df["conscientiousness"] = (4 - rows["i3"] + rows["i8"]) / 2
    df["neuroticism"] = (4 - rows["i4"] + rows["i9"]) / 2
    df["openness"] = (4 - rows["i5"] + rows["i10"]) / 2
    return df.sort_values("timestamp").drop_duplicates("participant_id", keep="first")


def parse_event_ratings(sub: pd.DataFrame) -> pd.DataFrame:
    """One row per participant per conference event (session or keynote)."""
    parts = []

    for letter in "ABCDEFGH":
        rows = sub[sub["survey_type"] == f"survey.session.{letter}.task"].copy()
        if rows.empty:
            continue
        att_col = _col(f"survey.session.attending.question.{letter}.step")
        rat_col = _col(f"survey.session.rating.question.{letter}.step")
        rows["rating_value"] = _value(rows[rat_col])
        rows["rating_text"] = _text(rows[rat_col])
        rows["attending_text"] = _text(rows[att_col])
        rows = rows[rows["rating_value"].notna()]
        if rows.empty:
            continue
        parts.append(rows[["participant_id", "timestamp", "attending_text",
                           "rating_value", "rating_text"]].assign(
            event_type="session", event_id=letter))

    for num in "123":
        rows = sub[sub["survey_type"] == f"survey.keynote.{num}.task"].copy()
        if rows.empty:
            continue
        rat_col = _col(f"survey.keynote.{num}.step")
        rows["rating_value"] = _value(rows[rat_col])
        rows["rating_text"] = _text(rows[rat_col])
        rows = rows[rows["rating_value"].notna()]
        if rows.empty:
            continue
        parts.append(rows[["participant_id", "timestamp",
                           "rating_value", "rating_text"]].assign(
            event_type="keynote", event_id=num, attending_text=None))

    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
