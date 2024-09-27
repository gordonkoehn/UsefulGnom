"""
Common code for unit testing of rules generated with Snakemake 8.18.2.
"""

from pathlib import Path
import subprocess as sp
import os
import pandas as pd

import sys


class OutputChecker:
    """
    Check the output of a Snakemake rule.
    """

    def __init__(self, data_path, expected_path, workdir):
        """
        Initialize the output checker.
        """
        self.data_path = data_path
        self.expected_path = expected_path
        self.workdir = workdir

    def check(self):
        """
        Check the output of the rule.
        """
        input_files = set(
            (Path(path) / f).relative_to(self.data_path)
            for path, subdirs, files in os.walk(self.data_path)
            for f in files
        )
        print("Input files: ", file=sys.stderr)
        print(input_files, file=sys.stderr)

        expected_files = set(
            (Path(path) / f).relative_to(self.expected_path)
            for path, subdirs, files in os.walk(self.expected_path)
            for f in files
        )

        print("Expected files: ", file=sys.stderr)
        print(expected_files, file=sys.stderr)

        unexpected_files = set()
        for path, subdirs, files in os.walk(self.workdir):
            for f in files:
                print("File: ", file=sys.stderr)
                print(f, file=sys.stderr)

                f = (Path(path) / f).relative_to(self.workdir)
                if str(f).startswith(".snakemake"):
                    continue
                if f in expected_files:
                    print("Comparing files: ", file=sys.stderr)
                    print(f, file=sys.stderr)

                    self.compare_files(self.workdir / f, self.expected_path / f)
                elif f in input_files:
                    # ignore input files
                    pass
                else:
                    unexpected_files.add(f)
        if unexpected_files:
            raise ValueError(
                "Unexpected files:\n{}".format(
                    "\n".join(sorted(map(str, unexpected_files)))
                )
            )

    def compare_files(self, generated_file, expected_file):
        """
        Compare the generated file with the expected file.
        """
        sp.check_output(["cmp", generated_file, expected_file])


def compare_csv_files(
    file1_path: str, file2_path: str, tolerance: float = 1e-4
) -> bool:
    """
    Compare two CSV files with a given tolerance.
    """
    df1 = pd.read_csv(file1_path, skiprows=[1])
    df2 = pd.read_csv(file2_path, skiprows=[1])

    if df1.shape != df2.shape:
        raise ValueError("DataFrames have different shapes")

    # check that the data frames contrain the same data types
    assert df1.dtypes.equals(df2.dtypes)

    # check that the data frames contain the same data
    pd.testing.assert_frame_equal(
        df1, df2, check_exact=False, rtol=tolerance, atol=tolerance
    )

    return True