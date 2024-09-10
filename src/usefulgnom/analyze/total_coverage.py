"""Implements the total coverage analysis.

    Credits:
        - core code: @AugusteRi (arimaite@ethz.ch)
        - implementation: @koehng (koehng@ethz.ch)
"""

from usefulgnom.serialize import load_convert_total
from usefulgnom.serialize.coverage import extract_sample_ID

from datetime import datetime
import pandas as pd
import glob
import re


def extract_mutation_position(mutations_of_interest_fp: str) -> list[str]:
    """
    Parse the mutation position read data from file.

    Args:
        mutations_of_interest_fp (str): Path to the mutations_of_interest file.

    Returns:
            list[str]: List of mutation positions.

    Raises:
        ValueError: If no match is found for the mutation.
    """

    datamatrix = pd.read_csv(mutations_of_interest_fp, usecols=["mut"])

    # Regex pattern to extract positions
    pattern = r"\d+"
    # Extract positions using regex
    # Result: list of positions
    extracted_data = []
    for mutation in datamatrix["mut"]:
        match = re.search(pattern, mutation)
        if match is None:
            raise ValueError(f"No match found for mutation: {mutation}")
        extracted_data.append(match.group())

    return extracted_data


def run_total_coverage_depth(
    coverage_tsv_fps: str,
    mutations_of_interest_fp: str,
    timeline_file_dir: str,
    output_file: str,
    startdate: str = "2024-01-01",
    enddate: str = "2024-07-03",
    location: str = "Zürich (ZH)",
) -> None:
    """
    Extract the coverage of the positions of interest from the coverage files.

    Args:
        coverage_tsv_fps (str): Path Pattern to the coverage.tsv.gz files.
            e.g.: cluster/project/pangolin/work-vp-test/variants/coverage.csv
        mutations_of_interest_fp (str): Path to the mutations of interest file.
        timeline_file_dir (str): Path to the timeline file.
        output_file (str): Path to the output file.
        startdate (str): Start date of the time period, default is 2024-01-01.
        enddate (str): End date of the time period, default is 2024-07-03.
        location (str): Location of the samples, default is Zürich (ZH).

    Returns:
        None
    """

    # Iterate over multiple coverage.tsv.gz files and take sample IDs, mutation
    # position, new nt, and number of reads
    # 1. Import mutations_of_interest csv file with mutations -> extract the
    #    positions and the mutated nt (from the rows)
    # 2. Take samples names (ID) from tsv file
    #    (pre-select time, protocol, location)
    # 3. Iterate over all directories with the name that is in the list of
    #     specified IDs:
    # 3.1 Open coverage.tsv.gz files for each sample
    # 3.2 Take the reads of each position and mutated nt
    # 3.3 Add this column to the matrix of coverage
    # 4. Output csv file

    # result: matrix
    # entries: how many reads cover that position

    # get list of coverage.tsv.gz files in the input directory
    coverage_files = glob.glob(coverage_tsv_fps, recursive=True)
    # get samples_IDs from the specified location, time and sequencing protocol
    startdatetime = datetime.strptime(startdate, "%Y-%m-%d")
    enddatetime = datetime.strptime(enddate, "%Y-%m-%d")
    sample_IDs = extract_sample_ID(
        timeline_file_dir, startdatetime, enddatetime, location
    )
    # get the position in the genome for which we want to find coverage
    position = extract_mutation_position(mutations_of_interest_fp)
    # record columns for df (one sample = one column of different mutations)
    columns = pd.DataFrame()
    # iterate over the basecnt.tsv.gz files from the list
    for cov_file in coverage_files:
        # extract the sample name from the directory name

        sample_name = cov_file.split("/")[-4]

        if sample_name in sample_IDs.loc[:, "sample"].values:
            # load the coverage.tsv.gz file of that sample,
            # and extract the column with the mutation coverages
            df = load_convert_total(cov_file, position)

            date = sample_IDs.loc[sample_IDs.loc[:, "sample"] == sample_name, "date"]

            columns[date] = df

    ind = pd.read_csv(mutations_of_interest_fp, usecols=["mut"])

    sorted_df = columns.sort_index(axis=1)
    # note that the index show the mutation
    # (actually we find total coverage per position = independent on the mutated nt)
    sorted_df = sorted_df.set_index(ind["mut"])
    sorted_df.to_csv(output_file)
