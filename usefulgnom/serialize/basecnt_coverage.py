"""Implements loading and converting the base nucleotide coverage data."""

import pandas as pd
import gzip


def load_convert(coverage_path: str, pos_mut: list[tuple]) -> pd.DataFrame:
    """
    Load and convert the base nucleotide coverage data.

    Args:
        coverage_path (str): Path to the coverage file.
        pos_mut (list[tuple]): List of tuples containing position and new nucleotide.

    Returns:
        pd.DataFrame: DataFrame containing the coverage data.

    """
    with gzip.open(coverage_path, "rt") as file:
        # Use pd.read_csv to read the file
        df = pd.read_csv(
            file, delimiter="\t", usecols=[1, 2, 3, 4, 5], header=None, index_col=None
        )[3:]
        df.columns = ["pos", "A", "C", "G", "T"]

    # extract coverage for specified positions and nt
    # position_mutation is a tuple (position, mutation)
    # record columns for df
    column = []
    for position_mutation in pos_mut:
        coverage = df.loc[df["pos"] == position_mutation[0], position_mutation[1]]

        column.append(coverage.iloc[0])

    df_out = pd.DataFrame(column)

    return df_out