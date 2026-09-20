from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"


def load_data():
    batches = pd.read_csv(DATA_DIR / "batches.csv", parse_dates=["Date", "Start", "End"])
    events = pd.read_csv(DATA_DIR / "downtime_events.csv")
    events = events.merge(batches[["Batch", "Operator", "Product", "Date"]], on="Batch", how="left")
    return batches, events


def kpis(batches):
    total_time = batches["Duration"].sum()
    return {
        "efficiency": batches["Min batch time"].sum() / total_time * 100,
        "total_time": total_time,
        "total_lost": batches["Lost Time"].sum(),
        "batches": len(batches),
        "days": batches["Date"].nunique(),
    }


def downtime_by_cause(events):
    table = (
        events.groupby(["Description", "Operator Error"])["Minutes"].sum()
        .reset_index()
        .sort_values("Minutes", ascending=False)
    )
    table["Share %"] = (table["Minutes"] / table["Minutes"].sum() * 100).round(1)
    return table

def operator_breakdown(batches, events):
    n = batches.groupby("Operator")["Batch"].count()
    lost = batches.groupby("Operator")["Lost Time"].sum()
    own = (
        events[events["Operator Error"] == "Yes"]
        .groupby("Operator")["Minutes"].sum()
        .reindex(n.index, fill_value=0)
    )
    table = pd.DataFrame({
        "Own errors": own / n,
        "Outside their control": (lost - own) / n,
    }).round(1)
    table.index.name = "Operator"
    table["Batches"] = n
    return table.reset_index().melt(
        id_vars=["Operator", "Batches"], var_name="Type", value_name="Min per batch"
    )


def product_summary(batches):
    table = batches.groupby("Product").agg(
        Batches=("Batch", "count"),
        Total_Time=("Duration", "sum"),
        Ideal_Time=("Min batch time", "sum"),
    )
    table["Efficiency %"] = (table["Ideal_Time"] / table["Total_Time"] * 100).round(1)
    return table.reset_index()