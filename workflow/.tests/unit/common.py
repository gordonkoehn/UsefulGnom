"""
Common code for unit testing of rules generated with Snakemake 8.18.2.
"""

from pathlib import Path
import subprocess as sp
import os
import pandas as pd
import numpy as np

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
    file1_path: str, file2_path: str, tolerance: float = 1e-5
) -> bool:
    """
    Compare two CSV files with a given tolerance.
    """
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    if df1.shape != df2.shape:
        return False

    for col in df1.columns:
        if df1[col].dtype in ["float64", "int64"]:
            if not np.allclose(df1[col], df2[col], rtol=tolerance, atol=tolerance):
                diff = df1[col] - df2[col]
                print(f"Differences in column {col}:\n{diff[diff.abs() > tolerance]}")
                print(
                    f"Raw values in {col} (file1):\n{df1[col][diff.abs() > tolerance]}"
                )
                print(
                    f"Raw values in {col} (file2):\n{df2[col][diff.abs() > tolerance]}"
                )
                return False
        else:
            if not (df1[col] == df2[col]).all():
                diff = df1[col] != df2[col]
                print(f"Differences in column {col}:\n{df1[diff]}")
                print(f"Raw values in {col} (file1):\n{df1[col][diff]}")
                print(f"Raw values in {col} (file2):\n{df2[col][diff]}")
                return False

    return True
