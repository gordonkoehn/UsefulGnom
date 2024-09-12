"""Shared serialization functions for coverage data."""

import pandas as pd
from datetime import datetime
from typing import Optional


def extract_sample_ID(
    timeline_file_dir: str,
    startdate: datetime = datetime.strptime("2024-01-01", "%Y-%m-%d"),
    enddate: datetime = datetime.strptime("2024-07-03", "%Y-%m-%d"),
    location: str = "Zürich (ZH)",
    protocol: Optional[str] = None,
) -> pd.DataFrame:
    """
    Extract the sample ID of the samples from selected time period,
    location, and protocol. extract the date of the samples.

    Seelects sampled from 2022-07 to 2023-03 and location Zürich by default.

    Args:
        timeline_file_dir (str): Path to the timeline file.
        startdate (datetime): Start date of the time period.
        enddate (datetime): End date of the time period.
        location (str): Location of the samples.
        protocol (str): Sequencing protocol used.
                         eg. for filtering condition to take
                             only Artic v4.1 protocol: "v41"

    Returns:
        pd.DataFrame: DataFrame containing the sample ID and date.
    """
    timeline_file = pd.read_csv(
        timeline_file_dir,
        sep="\t",
        usecols=["sample", "proto", "date", "location"],
        encoding="utf-8",
    )
    # convert the "date" column to datetime type:
    timeline_file["date"] = pd.to_datetime(timeline_file["date"])

    selected_rows = timeline_file[
        # TODO: remove subsample selection line below
        # (according to samples.wastewateronly.ready.tsv)
        (timeline_file["date"] > startdate.strftime("%Y-%m-%d"))
        & (timeline_file["date"] < enddate.strftime("%Y-%m-%d"))
        & (timeline_file["location"].isin([location]))
    ]
    if protocol is not None:
        selected_rows = selected_rows[(timeline_file["proto"] == protocol)]

    samples_ID = selected_rows[["sample", "date"]]
    return samples_ID
