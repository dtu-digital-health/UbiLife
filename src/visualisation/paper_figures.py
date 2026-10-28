"""Figures for the IEEE Pervasive Computing paper, built from data/processed and data/raw/parquet.

Usage: python -m src.visualisation.paper_figures <output_dir>
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw" / "parquet"

ACTIVITY_COLORS = {
    "STILL": "#bdbdbd",
    "WALKING": "#0072B2",
    "IN_VEHICLE": "#E69F00",
    "ON_BICYCLE": "#009E73",
    "RUNNING": "#D55E00",
}
SLEEP_HOURS = ["<6 hours", "6-8 hours", ">8 hours"]
SLEEP_QUALITY = ["Very Bad", "Bad", "Neutral", "Good", "Amazing"]


def _save(fig, out, name):
    fig.tight_layout()
    fig.savefig(out / name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def activity_by_hour(out):
    df = pd.read_parquet(PROCESSED / "activity.parquet")
    counts = (df.groupby([df["timestamp"].dt.hour, "measurement.data.type"]).size()
              .unstack(fill_value=0).reindex(range(24), fill_value=0)[list(ACTIVITY_COLORS)])
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.stackplot(counts.index, counts.T.values, labels=counts.columns,
                 colors=list(ACTIVITY_COLORS.values()), alpha=0.9)
    ax.set(xlim=(0, 23), xticks=range(0, 24, 3), xlabel="Hour of day (local Helsinki time)",
           ylabel="Activity records", title=f"Activity by hour (n={df['participant_id'].nunique()})")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    _save(fig, out, "01_activity_by_hour.png")


def wellbeing(out):
    sleep = pd.read_parquet(PROCESSED / "survey_daily_sleep.parquet")
    stress = pd.read_parquet(PROCESSED / "survey_daily_stress.parquet")["stress_level"]
    who5 = pd.read_parquet(PROCESSED / "survey_who5.parquet")["pct_score"]

    fig, axes = plt.subplots(1, 4, figsize=(16, 3.6))
    sleep["sleep_hours_text"].value_counts().reindex(SLEEP_HOURS, fill_value=0).plot.bar(ax=axes[0], rot=0)
    axes[0].set(xlabel="", ylabel="Responses", title=f"(a) Sleep duration (n={len(sleep)})")
    sleep["sleep_quality_text"].value_counts().reindex(SLEEP_QUALITY, fill_value=0).plot.bar(ax=axes[1], rot=0)
    axes[1].set(xlabel="", ylabel="Responses", title=f"(b) Sleep quality (n={len(sleep)})")

    axes[2].hist(stress, bins=np.arange(-0.5, 11.5, 1), edgecolor="white")
    axes[2].axvline(stress.median(), color="red", ls="--", label=f"median={stress.median():.0f}")
    axes[2].set(xlabel="Stress (0-10)", ylabel="Responses", xticks=range(0, 11, 2),
                title=f"(c) Daily stress (n={len(stress)})")
    axes[2].legend(fontsize=8)

    axes[3].hist(who5, bins=np.arange(0, 104, 8), edgecolor="white")
    axes[3].axvline(who5.median(), color="red", ls="--", label=f"median={who5.median():.0f}%")
    axes[3].axvline(50, color="orange", ls=":", label="at-risk threshold (50%)")
    axes[3].set(xlabel="WHO-5 score (%)", ylabel="Participants", xlim=(0, 100),
                title=f"(d) WHO-5 wellbeing (n={len(who5)})")
    axes[3].legend(fontsize=8)
    _save(fig, out, "01_wellbeing.png")


def devices(out):
    cols = ["measurement.sensorStartTime", "dataStream.studyDeploymentId", "measurement.data.platform",
            "measurement.data.deviceManufacturer", "measurement.data.hardware"]
    df = (pd.read_parquet(RAW / "deviceinformation.parquet", columns=cols)
          .sort_values(cols[0]).groupby(cols[1]).last())
    platform, maker, hardware = (df[c] for c in cols[2:])
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    platform.value_counts().plot.pie(ax=ax1, autopct=lambda p: f"{p:.0f}%\n({p * len(df) / 100:.0f})")
    ax1.set(ylabel="", title=f"Platform (n={len(df)})")
    maker.str.capitalize().replace({"Oneplus": "OnePlus"}).value_counts().sort_values().plot.barh(ax=ax2)
    ax2.set(xlabel="Participants", ylabel="", title="Manufacturer")
    hardware.value_counts().head(10).sort_values().plot.barh(ax=ax3)
    ax3.set(xlabel="Participants", ylabel="", title="Top 10 hardware models")
    _save(fig, out, "01_devices.png")


if __name__ == "__main__":
    sns.set_theme(style="whitegrid", palette="husl")
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "reports" / "figures" / "paper")
    out.mkdir(parents=True, exist_ok=True)
    for make in (activity_by_hour, wellbeing, devices):
        make(out)
    print(f"Saved to {out}")
