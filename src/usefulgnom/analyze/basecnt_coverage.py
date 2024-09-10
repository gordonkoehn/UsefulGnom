"""Implements the read coverage analysis."""

from usefulgnom.serialize.basecnt_coverage import load_convert

from typing import Optional

from datetime import datetime
import pandas as pd
import re
import glob
import pathlib


def extract_mutation_position_and_nt(datamatrix_dir: str) -> list[tuple]:
    """
    Parse the mutation-position read data from file.

    Args:
        datamatrix_dir (str): Path to the datamatrix file.

    Returns:
        list[tuple]: List of tuples containing mutation position and new nucleotide.

    Raises:
        ValueError: If no match is found for the mutation.
    """

    # make sure datamatrix_dir is a filepath
    datamatrix_fp = pathlib.Path(datamatrix_dir)

    # Read the CSV file
    datamatrix = pd.read_csv(datamatrix_fp, usecols=["mut"])

    # Regex pattern to extract positions and new (mutated) nucleotides
    pattern = r"(\d+)([A-Z])"
    # Extract positions and new nucleotides using regex
    # Result is list of tuples: position and new nucleotide
    extracted_data = []
    for mutation in datamatrix["mut"]:
        match = re.search(pattern, mutation)
        if match is None:
            raise ValueError(f"No match found for mutation: {mutation}")
        extracted_data.append((match.group(1), match.group(2)))

    return extracted_data


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


def run_basecnt_coverage(
    basecnt_fps: str,
    timeline_file_dir: str,
    datamatrix_dir: str,
    output_file: str,
    startdate: datetime = datetime.strptime("2024-01-01", "%Y-%m-%d"),
    enddate: datetime = datetime.strptime("2024-07-03", "%Y-%m-%d"),
    location: str = "Zürich (ZH)",
) -> None:
    """
    Analyze the read nucleotide coverage data.

    Args:
        basecnt_fps list[str]: List of paths to the basecnt.tsv.gz files.
        '...work-ww-lofreq-230405/results/*/*/alignments/basecnt.tsv.gz'
        timeline_file_dir (str): Path to the timeline file.
        datamatrix_dir (str): Path to the datamatrix file.
        output_file (str): Path to the output file.
        startdate (datetime): Start date of the time period, default is 2024-01-01.
        enddate (datetime): End date of the time period, default is 2024-07-03.
        location (str): Location of the samples, default is Zürich (ZH).

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
    coverage_files = glob.glob(basecnt_fps, recursive=True)

    # get samples_IDs from the specified location, time and sequencing protocol
    sample_IDs = extract_sample_ID(timeline_file_dir, startdate, enddate, location)
    # get the position in the genome and mutated nt for which we want to
    #  find coverage
    position_mutated_nt = extract_mutation_position_and_nt(datamatrix_dir)

    # record columns for df (one sample = one column of different mutations)
    columns = pd.DataFrame()
    # iterate over the basecnt.tsv.gz files from the list
    for basecnt_file in coverage_files:
        # extract the sample name from the directory name
        sample_name = basecnt_file.split("/")[-4]
        if sample_name in sample_IDs.iloc[:, 0].values:
            # load the basecnt.tsv.gz file of that sample, and extract the
            # column with the mutation coverages
            df = load_convert(basecnt_file, position_mutated_nt)
            date = sample_IDs.loc[sample_IDs.loc[:, "sample"] == sample_name, "date"]
            columns[date] = df

    # wrangle the data to have the same order of columns as in the datamatrix
    ind = pd.read_csv(datamatrix_dir, usecols=["mut"])
    sorted_df = columns.sort_index(axis=1)
    sorted_df = sorted_df.set_index(ind["mut"])
    # save the output to a csv file
    sorted_df.to_csv(output_file)
