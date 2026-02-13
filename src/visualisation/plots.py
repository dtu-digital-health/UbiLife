"""Plot functions for UbiLife dataset exploration."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _save(fig, save_dir, name):
    fig.tight_layout()
    fig.savefig(save_dir / name, dpi=150, bbox_inches="tight")
    plt.show()


def plot_stream_overview(overview_df, save_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    sns.barplot(data=overview_df, y="stream", x="records", ax=ax1)
    ax1.set_xscale("log")
    ax1.set(xlabel="Records (log)", title="Records per Stream")
    sns.barplot(data=overview_df, y="stream", x="participants", ax=ax2)
    ax2.set(xlabel="Participants", title="Participants per Stream")
    _save(fig, save_dir, "01_stream_overview.png")


def plot_daily_volume(stream_dfs, save_dir):
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    for ax, (name, df) in zip(axes.flat, stream_dfs.items()):
        daily = df.set_index("timestamp").resample("D").size()
        ax.bar(daily.index, daily.values)
        ax.set(title=name, ylabel="Records")
        ax.tick_params(axis="x", rotation=30)
    _save(fig, save_dir, "01_daily_volume.png")


def plot_participant_spans(participant_spans, save_dir):
    fig, ax = plt.subplots(figsize=(14, 8))
    norm = plt.Normalize(participant_spans["count"].min(), participant_spans["count"].max())
    for i, (_, row) in enumerate(participant_spans.iterrows()):
        ax.barh(i, row["days_active"], left=row["min"], height=0.7,
                color=plt.cm.RdYlGn(norm(row["count"])))
    ax.set(yticks=[], xlabel="Date", title="Per-Participant Active Period (step data)")
    ax.axvspan("2025-10-13", "2025-10-17", alpha=0.1, color="blue", label="Conference week")
    ax.legend(loc="lower right")
    plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap="RdYlGn"), ax=ax, label="Step records")
    _save(fig, save_dir, "01_participant_spans.png")


def plot_records_per_participant(stream_dfs, save_dir):
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    for ax, (name, df) in zip(axes.flat, stream_dfs.items()):
        counts = df.groupby("participant_id").size().sort_values(ascending=False)
        ax.bar(range(len(counts)), counts.values)
        ax.axhline(counts.median(), color="red", ls="--", label=f"median={counts.median():,.0f}")
        ax.set(title=name, xlabel="Participant (ranked)", ylabel="Records")
        ax.legend(fontsize=8)
    _save(fig, save_dir, "01_records_per_participant.png")


def plot_step_cumulative_vs_delta(one_p, save_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))
    ax1.plot(one_p["timestamp"], one_p["steps"], lw=0.5)
    ax1.set(title="Raw Step Count (cumulative)", ylabel="Steps")
    ax2.plot(one_p["timestamp"], one_p["step_delta"], lw=0.5)
    ax2.set(title="Step Deltas (diff, clipped >=0)", ylabel="Steps/interval")
    _save(fig, save_dir, "01_step_cumulative_vs_delta.png")


def plot_activity_types(df_activity, save_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    df_activity["activity_type"].value_counts().plot.barh(ax=ax1)
    ax1.set(xlabel="Records", title="Activity Type Distribution")
    df = df_activity.copy()
    df["hour"] = df["timestamp"].dt.hour
    df.groupby(["hour", "activity_type"]).size().unstack(fill_value=0).plot.area(ax=ax2, alpha=0.7)
    ax2.set(xlabel="Hour", ylabel="Records", title="Activity by Hour")
    ax2.legend(fontsize=7)
    _save(fig, save_dir, "01_activity_types.png")


def plot_devices(df_device, save_dir):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    df_device["platform"].value_counts().plot.pie(ax=ax1, autopct="%1.0f%%")
    ax1.set(ylabel="", title="Platform")
    df_device["manufacturer"].value_counts().plot.barh(ax=ax2)
    ax2.set(xlabel="Reports", title="Manufacturer")
    df_device["hardware"].value_counts().head(10).plot.barh(ax=ax3)
    ax3.set(xlabel="Reports", title="Top 10 Hardware")
    _save(fig, save_dir, "01_devices.png")


def plot_survey_overview(df_survey, submitted, save_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ct = df_survey.groupby(["survey_type", "status"]).size().unstack(fill_value=0)
    ct.plot.barh(stacked=True, ax=ax1, color={"submitted": "#4CAF50", "canceled": "#F44336"})
    ax1.set(xlabel="Responses", title="Submissions vs Cancellations")
    submitted.set_index("timestamp").resample("D")["status"].count().plot.bar(ax=ax2)
    ax2.set(ylabel="Surveys", title="Submissions Over Time")
    _save(fig, save_dir, "01_survey_overview.png")


def plot_demographics(ages, genders, roles, prior, save_dir):
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    axes[0, 0].hist(ages, bins=range(20, 65, 3))
    axes[0, 0].axvline(np.median(ages), color="red", ls="--", label=f"median={np.median(ages):.0f}")
    axes[0, 0].set(xlabel="Age", ylabel="Count", title=f"Age (n={len(ages)})")
    axes[0, 0].legend()
    pd.Series(genders).value_counts().plot.pie(ax=axes[0, 1], autopct="%1.0f%%")
    axes[0, 1].set(ylabel="", title=f"Gender (n={len(genders)})")
    pd.Series(roles).value_counts().plot.barh(ax=axes[1, 0])
    axes[1, 0].set(xlabel="Count", title=f"Role (n={len(roles)})")
    pd.Series(prior).value_counts().plot.barh(ax=axes[1, 1])
    axes[1, 1].set(xlabel="Count", title=f"Prior UbiComp (n={len(prior)})")
    _save(fig, save_dir, "01_demographics.png")


def plot_daily_surveys(stress_vals, sleep_quality_texts, sleep_hour_texts, save_dir):
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    ax1.hist(stress_vals, bins=np.arange(-0.5, 11.5, 1))
    ax1.axvline(np.median(stress_vals), color="red", ls="--", label=f"median={np.median(stress_vals):.1f}")
    ax1.set(xlabel="Stress (0-10)", ylabel="Responses", title=f"Stress (n={len(stress_vals)})")
    ax1.legend()
    quality_order = ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"]
    sq = pd.Series(sleep_quality_texts).value_counts()
    sq.reindex([q for q in quality_order if q in sq.index]).plot.barh(ax=ax2)
    ax2.set(xlabel="Responses", title=f"Sleep Quality (n={len(sleep_quality_texts)})")
    hours_order = ["<6 hours", "6-7 hours", "7-8 hours", "8-9 hours", ">9 hours"]
    sh = pd.Series(sleep_hour_texts).value_counts()
    sh.reindex([h for h in hours_order if h in sh.index]).plot.barh(ax=ax3)
    ax3.set(xlabel="Responses", title=f"Sleep Duration (n={len(sleep_hour_texts)})")
    _save(fig, save_dir, "01_daily_surveys.png")


def plot_who5_bfi10(who5_scores, bfi_dimensions, save_dir):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    if who5_scores:
        who5_df = pd.DataFrame(who5_scores)
        ax1.hist(who5_df["pct_score"], bins=12)
        ax1.axvline(who5_df["pct_score"].median(), color="red", ls="--", label=f'median={who5_df["pct_score"].median():.0f}%')
        ax1.axvline(50, color="orange", ls=":", label="Threshold (50%)")
        ax1.set(xlabel="WHO-5 Score (%)", ylabel="Participants", title=f"WHO-5 (n={len(who5_df)})")
        ax1.legend(fontsize=8)
    if bfi_dimensions:
        bfi_df = pd.DataFrame(bfi_dimensions)
        dims = ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]
        bfi_df[dims].plot.box(vert=False, ax=ax2)
        ax2.set(xlabel="Score (0-4)", title=f"BFI-10 (n={len(bfi_df)})")
    _save(fig, save_dir, "01_who5_bfi10.png")


def plot_session_ratings(session_ratings, save_dir):
    if not session_ratings:
        print("No session rating data found")
        return
    sr_df = pd.DataFrame(session_ratings)
    rating_order = ["Boring", "Slightly Boring", "Neutral", "Interesting", "Very Interesting"]
    ct = pd.crosstab(sr_df["session"], sr_df["rating"]).reindex(columns=rating_order, fill_value=0)
    fig, ax = plt.subplots(figsize=(12, 5))
    ct.plot.barh(stacked=True, ax=ax)
    ax.set(xlabel="Responses", title="Session Ratings")
    ax.legend(fontsize=8, bbox_to_anchor=(1.02, 1))
    _save(fig, save_dir, "01_session_ratings.png")


def plot_weather(df_weather, save_dir):
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    daily = df_weather.set_index("timestamp").resample("D")["temperature"].agg(["mean", "min", "max"])
    axes[0, 0].fill_between(daily.index, daily["min"], daily["max"], alpha=0.3)
    axes[0, 0].plot(daily.index, daily["mean"])
    axes[0, 0].set(ylabel="Temp (C)", title="Daily Temperature")
    df_weather["weather_main"].value_counts().plot.barh(ax=axes[0, 1])
    axes[0, 1].set(xlabel="Records", title="Weather Conditions")
    axes[1, 0].hist(df_weather["humidity"].dropna(), bins=30)
    axes[1, 0].set(xlabel="Humidity (%)", title="Humidity")
    axes[1, 1].hist(df_weather["wind_speed"].dropna(), bins=30)
    axes[1, 1].set(xlabel="Wind Speed (m/s)", title="Wind Speed")
    _save(fig, save_dir, "01_weather.png")
