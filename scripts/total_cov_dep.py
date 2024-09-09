import pandas as pd
import argparse
import glob
import gzip
import re


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


# Extract sample ID of the samples from selected time period, location, and protocol
# extract the date of the samples
def extract_sample_ID(timeline_file_dir):
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


def load_convert(coverage_path, pos):
    with gzip.open(coverage_path, "rt") as file:
        # Use pd.read_csv to read the file
        df = pd.read_csv(
            file, delimiter="\t", usecols=[1, 2], header=None, index_col=None
        )[1:]

        df.columns = ["pos", "coverage"]

    # extract coverage for specified position and nt
    # record columns for df
    column = []
    for position in pos:
        coverage = df.loc[df["pos"] == position, "coverage"]

        column.append(coverage.iloc[0])

    df_out = pd.DataFrame(column)

    return df_out


def main(coverage_tsv_dir, datamatrix_dir, timeline_file_dir, output_file):
    # get list of coverage.tsv.gz files in the input directory
    coverage_files = glob.glob(coverage_tsv_dir, recursive=True)
    # get samples_IDs from the specified location, time and sequencing protocol
    sample_IDs = extract_sample_ID(timeline_file_dir)
    # get the position in the genome for which we want to find coverage
    position = extract_mutation_position(datamatrix_dir)
    # record columns for df (one sample = one column of different mutations)
    ###columns = []
    columns = pd.DataFrame()
    # iterate over the basecnt.tsv.gz files from the list
    for cov_file in coverage_files:
        # extract the sample name from the directory name

        sample_name = cov_file.split("/")[-4]

        if sample_name in sample_IDs.loc[:, "sample"].values:
            # load the coverage.tsv.gz file of that sample, and extract the column with the mutation coverages
            df = load_convert(cov_file, position)

            date = sample_IDs.loc[sample_IDs.loc[:, "sample"] == sample_name, "date"]

            columns[date] = df

    ###df_out = pd.concat(columns, ignore_index = True, axis = 1)
    ind = pd.read_csv(datamatrix_dir, usecols=["mut"])

    sorted_df = columns.sort_index(axis=1)
    # note that the index show the mutation (actually we find total coverage per position = independent on the mutated nt)
    sorted_df = sorted_df.set_index(ind["mut"])
    sorted_df.to_csv(output_file)

    # columns.to_csv(output_file, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process coverage.tsv.gz files and make position coverage matrix"
    )
    parser.add_argument(
        "coverage_tsv_dir",
        help="input directory containing general coverage.tsv.gz files: it should be: "
        "/cluster/project/pangolin/work-vp-test/results/*/*/alignments/coverage.tsv.gz",
    )
    parser.add_argument(
        "datamatrix_dir",
        help="input directory of the datamatrix csv file with relevant mutations",
    )
    parser.add_argument(
        "timeline_file_dir", help="input directory of the timeline tsv file"
    )

    parser.add_argument(
        "output_file",
        help="output CSV file: total coverage of that position over the time",
    )

    args = parser.parse_args()

    main(
        args.coverage_tsv_dir, # acutally coverage.tsv.gz
        args.datamatrix_dir,
        args.timeline_file_dir,
        args.output_file,
    )

## use coverage.tsv !!!