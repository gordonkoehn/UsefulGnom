"""Implements the read coverage analysis.

    Credits:
        - core code: @AugusteRi (arimaite@ethz.ch)
        - implementation: @koehng (koehng@ethz.ch)
"""

from usefulgnom.serialize import load_convert_bnc
from usefulgnom.serialize.coverage import extract_sample_ID


from datetime import datetime
import pandas as pd
import re
import glob
import pathlib


def extract_mutation_position_and_nt(mutations_of_interest_dir: str) -> list[tuple]:
    """
    Parse the mutation-position read data from file.

    Args:
        mutations_of_interest_dir (str): Path to the mutations_of_interest file.

    Returns:
        list[tuple]: List of tuples containing mutation position and new nucleotide.

    Raises:
        ValueError: If no match is found for the mutation.
    """

    # make sure mutations_of_interest_dir is a filepath
    mutations_of_interest_fp = pathlib.Path(mutations_of_interest_dir)

    # Read the CSV file
    mutations_of_interest = pd.read_csv(mutations_of_interest_fp, usecols=["mut"])

    # Regex pattern to extract positions and new (mutated) nucleotides
    pattern = r"(\d+)([A-Z])"
    # Extract positions and new nucleotides using regex
    # Result is list of tuples: position and new nucleotide
    extracted_data = []
    for mutation in mutations_of_interest["mut"]:
        match = re.search(pattern, mutation)
        if match is None:
            raise ValueError(f"No match found for mutation: {mutation}")
        extracted_data.append((match.group(1), match.group(2)))

    return extracted_data


def run_basecnt_coverage(
    basecnt_fps: str,
    timeline_file_dir: str,
    mutations_of_interest_dir: str,
    output_file: str,
    startdate: str = "2024-01-01",
    enddate: str = "2024-07-03",
    location: str = "Zürich (ZH)",
) -> None:
    """
    Analyze the read nucleotide coverage data.

    Args:
        basecnt_fps list[str]: List of paths to the basecnt.tsv.gz files.
        '...work-ww-lofreq-230405/results/*/*/alignments/basecnt.tsv.gz'
        timeline_file_dir (str): Path to the timeline file.
        mutations_of_interest_dir (str): Path to the mutations_of_interest file.
        output_file (str): Path to the output file.
        startdate (str): Start date of the time period, default is 2024-01-01.
        enddate (str): End date of the time period, default is 2024-07-03.
        location (str): Location of the samples, default is Zürich (ZH).

    Returns:
        None

    """
    # Iterate over multiple basecnt.tsv.gz files and take sample IDs,
    #  mutation position, new nt, and number of reads
    # 1. Import mutations_of_interest csv file with mutations-> extract the positions,
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
    startdatetime = datetime.strptime(startdate, "%Y-%m-%d")
    enddatetime = datetime.strptime(enddate, "%Y-%m-%d")
    sample_IDs = extract_sample_ID(
        timeline_file_dir, startdatetime, enddatetime, location
    )
    # get the position in the genome and mutated nt for which we want to
    #  find coverage
    position_mutated_nt = extract_mutation_position_and_nt(mutations_of_interest_dir)

    # record columns for df (one sample = one column of different mutations)
    columns = pd.DataFrame()
    # iterate over the basecnt.tsv.gz files from the list
    for basecnt_file in coverage_files:
        # extract the sample name from the directory name
        sample_name = basecnt_file.split("/")[-4]
        if sample_name in sample_IDs.iloc[:, 0].values:
            # load the basecnt.tsv.gz file of that sample, and extract the
            # column with the mutation coverages
            df = load_convert_bnc(basecnt_file, position_mutated_nt)
            date = sample_IDs.loc[sample_IDs.loc[:, "sample"] == sample_name, "date"]
            columns[date] = df

    # wrangle the data to have the same order of columns as in the mutations_of_interest
    ind = pd.read_csv(mutations_of_interest_dir, usecols=["mut"])
    sorted_df = columns.sort_index(axis=1)
    sorted_df = sorted_df.set_index(ind["mut"])
    # save the output to a csv file
    sorted_df.to_csv(output_file)
