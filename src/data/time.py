"""Timestamp handling: CARP sensorStartTime is epoch µs in UTC."""

import pandas as pd

# UbiComp 2025, Espoo. Confirmed by survey endDate (device-local) = UTC+3 for 49/59 participants.
LOCAL_TZ = "Europe/Helsinki"


def to_local(us: pd.Series) -> pd.Series:
    """Epoch microseconds (UTC) → naive local conference time."""
    return (
        pd.to_datetime(us, unit="us", utc=True, errors="coerce")
        .dt.tz_convert(LOCAL_TZ)
        .dt.tz_localize(None)
    )


def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add `timestamp` (local) and `participant_id` from raw CARP columns."""
    df["timestamp"] = to_local(df["measurement.sensorStartTime"])
    df["participant_id"] = df["dataStream.studyDeploymentId"]
    return df
