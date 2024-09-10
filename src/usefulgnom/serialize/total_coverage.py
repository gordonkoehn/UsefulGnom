"""Implements loading and converting the total coverage data.

e.g. of total coverage file (coverage.tsv):

ref	pos	B3_25_2024_08_11/20240823_2346503305
NC_045512.2	1	0
NC_045512.2	2	0
NC_045512.2	3	0
NC_045512.2	4	0
NC_045512.2	5	0

"""

import pandas as pd
import gzip


def load_convert_total(
        coverage_path : str,
        pos : list[str]
        ) -> pd.DataFrame:
    """
    Load and convert the total coverage data.
    """

    with gzip.open(coverage_path, 'rt') as file:

        # Use pd.read_csv to read the file
        df = pd.read_csv(file, delimiter='\t', usecols=[1, 2], header=None, index_col=None)[1:]

        df.columns = ['pos', 'coverage']

    # extract coverage for specified position and nt
    # record columns for df
    column = []
    for position in pos:
        coverage = (df.loc[df['pos'] == position, 'coverage'])

        column.append(coverage.iloc[0])

    df_out = pd.DataFrame(column)

    return df_out