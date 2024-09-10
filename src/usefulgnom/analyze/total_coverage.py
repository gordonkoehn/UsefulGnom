"""Implements the total coverage analysis.

    Credits:
        - core code: @AugusteRi (arimaite@ethz.ch)
        - implementation: @koehng (koehng@ethz.ch)
"""

from usefulgnom.serialize import load_convert_total

import pandas as pd
import glob
import re


def extract_mutation_position(datamatrix_dir):
    datamatrix = pd.read_csv(datamatrix_dir, usecols=["mut"])

    # Regex pattern to extract positions
    pattern = r"\d+"
    # Extract positions using regex
    # Result: list of positions
    extracted_data = [
        re.search(pattern, mutation).group() for mutation in datamatrix["mut"]
    ]

    return extracted_data


def extract_sample_ID(timeline_file_dir):
    """
    Extract the sample ID of the samples from selected time period, location, and protocol.
    Extract the date of the samples.
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
        # select the rows with date from 2024-01 to 2024-07 (according to .tsv file)
        (timeline_file["date"] > "2024-01-01")
        & (timeline_file["date"] < "2024-07-03")
        & (timeline_file["location"].isin(["Zürich (ZH)"]))  # & # only Zurich
        # filtering condition to take only Artic v4.1 protocol:
        # (timeline_file["proto"] == "v41")
    ]
    samples_ID = selected_rows[["sample", "date"]]
    return samples_ID


def run_total_coverage_depth(
    coverage_tsv_fps: str,
    mutations_of_interest_fp: str,
    timeline_file_dir: str,
    output_file: str,
):
    # Iterate over multiple coverage.tsv.gz files and take sample IDs, mutation position, new nt, and number of reads
    # 1. Import datamatrix csv file with mutations -> extract the positions and the mutated nt (from the rows)
    # 2. Take samples names (ID) from tsv file (pre-select time, protocol, location)
    # 3. Iterate over all directories with the name that is in the list of specified IDs:
    # 3.1 Open coverage.tsv.gz files for each sample
    # 3.2 Take the reads of each position and mutated nt
    # 3.3 Add this column to the matrix of coverage
    # 4. Output csv file

    # result: matrix
    # entries: how many reads cover that position

    # get list of coverage.tsv.gz files in the input directory
    coverage_files = glob.glob(coverage_tsv_fps, recursive=True)
    # get samples_IDs from the specified location, time and sequencing protocol
    sample_IDs = extract_sample_ID(timeline_file_dir)
    # get the position in the genome for which we want to find coverage
    position = extract_mutation_position(mutations_of_interest_fp)
    # record columns for df (one sample = one column of different mutations)
    columns = pd.DataFrame()
    # iterate over the basecnt.tsv.gz files from the list
    for cov_file in coverage_files:
        # extract the sample name from the directory name

        sample_name = cov_file.split("/")[-4]

        if sample_name in sample_IDs.loc[:, "sample"].values:
            # load the coverage.tsv.gz file of that sample, and extract the column with the mutation coverages
            df = load_convert_total(cov_file, position)

            date = sample_IDs.loc[sample_IDs.loc[:, "sample"] == sample_name, "date"]

            columns[date] = df

    ind = pd.read_csv(mutations_of_interest_fp, usecols=["mut"])

    sorted_df = columns.sort_index(axis=1)
    # note that the index show the mutation (actually we find total coverage per position = independent on the mutated nt)
    sorted_df = sorted_df.set_index(ind["mut"])
    sorted_df.to_csv(output_file)
