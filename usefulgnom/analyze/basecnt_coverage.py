"""Implements the read coverage analysis."""

from usefulgnom.serialize.basecnt_coverage import load_convert

import pandas as pd
import re
import glob


def extract_mutation_position_and_nt(datamatrix_dir: str) -> list[tuple]:
    """
    Parse the mutation-position read data from file.

    Args:
        datamatrix_dir (str): Path to the datamatrix file.

    Returns:
        list[tuple]: List of tuples containing mutation position and new nucleotide.
    """
    # TODO: change path to pathlib.Path

    datamatrix = pd.read_csv(datamatrix_dir, usecols=["mut"])

    # Regex pattern to extract positions and new (mutated) nucleotides
    pattern = r"(\d+)([A-Z])"
    # Extract positions and new nucleotides using regex
    # Result is list of tuples: position and new nucleotide
    extracted_data = [
        (re.search(pattern, mutation).group(1), re.search(pattern, mutation).group(2))
        for mutation in datamatrix["mut"]
    ]

    return extracted_data


def extract_sample_ID(timeline_file_dir: str) -> pd.DataFrame:
    """
    Extract the sample ID of the samples from selected time period,
    location, and protocol. extract the date of the samples.

    Args:
        timeline_file_dir (str): Path to the timeline file.

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
        # select the rows with date from 2022-07 to 2023-03
        # (according to samples.wastewateronly.ready.tsv)
        (timeline_file["date"] > "2024-01-01")
        & (timeline_file["date"] < "2024-07-03")
        & (timeline_file["location"].isin(["Zürich (ZH)"]))  # & # only Zurich
        # e.g. filtering condition to take only Artic v4.1 protocol:
        # (timeline_file["proto"] == "v41")
    ]
    samples_ID = selected_rows[["sample", "date"]]
    return samples_ID


def run_basecnt_coverage(
    coverage_fps: str,
    timeline_file_dir: str,
    datamatrix_dir: str,
    output_file: str,
) -> None:
    """
    Analyze the read nucleotide coverage data.

    Args:
        coverage_fps list[str]: List of paths to the basecnt.tsv.gz files.
        '...work-ww-lofreq-230405/results/*/*/alignments/basecnt.tsv.gz'
        timeline_file_dir (str): Path to the timeline file.
        datamatrix_dir (str): Path to the datamatrix file.
        output_file (str): Path to the output file.

    Returns:
        None

    """

    # Iterate over multiple basecnt.tsv.gz files and take sample IDs,
    #  mutation position, new nt, and number of reads
    # 1. Import datamatrix csv file with mutations-> extract the positions,
    #  and the mutated nt (from the rows)
    # 2. Take samples names (ID) from tsv file (pre-select time, protocol,
    #    location)
    # 3. Iterate over all directories with the name that is in the list
    #    of specified IDs:
    #   3.1 Open basecnt.tsv.gz files for each sample
    #   3.2 Take the reads of each position and mutated nt
    #   3.3 Add this column to the matrix of coverage
    # 4. Output csv file

    # get list of base coverage basecnt.tsv.gz files in the input directory
    coverage_files = glob.glob(coverage_fps, recursive=True)

    # get samples_IDs from the specified location, time and sequencing protocol
    sample_IDs = extract_sample_ID(timeline_file_dir)
    # get the position in the genome and mutated nt for which we want to
    #  find coverage
    position_mutated_nt = extract_mutation_position_and_nt(datamatrix_dir)

    # record columns for df (one sample = one column of different mutations)
    # columns = []
    columns = pd.DataFrame()
    # iterate over the basecnt.tsv.gz files from the list
    for basecnt_file in coverage_files:
        # extract the sample name from the directory name
        # print(basecnt_file)
        sample_name = basecnt_file.split("/")[-4]
        if sample_name in sample_IDs.iloc[:, 0].values:
            # print(sample_name)

            # load the basecnt.tsv.gz file of that sample, and extract the
            # column with the mutation coverages
            df = load_convert(basecnt_file, position_mutated_nt)

            date = sample_IDs.loc[sample_IDs.loc[:, "sample"] == sample_name, "date"]

            columns[date] = df

    ###df_out = pd.concat(columns, ignore_index = True, axis = 1)
    ind = pd.read_csv(datamatrix_dir, usecols=["mut"])

    sorted_df = columns.sort_index(axis=1)
    sorted_df = sorted_df.set_index(ind["mut"])

    sorted_df.to_csv(output_file)
    # columns.to_csv(output_file, index=False)
