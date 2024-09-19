"""
Test the make_price_data rule.
"""
import os
import sys

import subprocess as sp
from tempfile import TemporaryDirectory
import shutil
from pathlib import Path, PurePosixPath

sys.path.insert(0, os.path.dirname(__file__))


def test_make_price_data():
    """Test the make_price_data rule."""
    with TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir) / "workdir"
        data_path = PurePosixPath(".tests/unit/make_price_data/data")
        expected_path = PurePosixPath(".tests/unit/make_price_data/expected")

        # Copy data to the temporary workdir.
        shutil.copytree(data_path, workdir / ".." / "data")

        # dbg
        print("../data/statistics.csv", file=sys.stderr)
        # print out the current working directory
        print("Current working directory: ", file=sys.stderr)
        print(os.getcwd(), file=sys.stderr)
        # print the content of the workdir

        # Run the test job.
        sp.check_output(
            [
                "python",
                "-m",
                "snakemake",
                "../data/statistics.csv",
                "-f",
                "-j1",
                "--target-files-omit-workdir-adjustment",
                "--directory",
                workdir,
            ]
        )

        # print the content of the workdir
        print(os.listdir(workdir), file=sys.stderr)

        # show the contents of the temporary workdir
        print("Contents of the temporary workdir: ", file=sys.stderr)
        for root, dirs, files in os.walk(workdir):
            print(f"root: {root}", file=sys.stderr)
            print(f"dirs: {dirs}", file=sys.stderr)
            print(f"files: {files}", file=sys.stderr)

        # let's see the contents of the generated file - header, firt few lines
        print("Generated file: ", file=sys.stderr)
        with open(workdir / ".." / "data" / "statistics.csv") as f:
            print(f.readline(), file=sys.stderr)
            print(f.readline(), file=sys.stderr)
            print(f.readline(), file=sys.stderr)

        # let's see the contents of the expected file - header, firt few lines
        print("Expected file: ", file=sys.stderr)
        with open(expected_path / "statistics.csv") as f:
            print(f.readline(), file=sys.stderr)
            print(f.readline(), file=sys.stderr)
            print(f.readline(), file=sys.stderr)

        # Check the output files against the expected files in python.
        try:
            # check if the paths are correct print otherwise
            print("workdir / .. / data / statistics.csv: ", file=sys.stderr)
            print(workdir / ".." / "data" / "statistics.csv", file=sys.stderr)
            print("expected_path / statistics.csv: ", file=sys.stderr)
            print(expected_path / "statistics.csv", file=sys.stderr)
            # check if the files are the same
            sp.check_output(
                [
                    "diff",
                    workdir / ".." / "data" / "statistics.csv",
                    expected_path / "statistics.csv",
                ]
            )
            print("Files are the same.")
        except sp.CalledProcessError:
            print("Files are different. Showing differences:")
            diff_output = sp.check_output(
                [
                    "diff",
                    workdir / ".." / "data" / "statistics.csv",
                    expected_path / "statistics.csv",
                ]
            )
            print(diff_output.decode())
            raise ValueError("Files are different.")

        # Check the output byte by byte using cmp.
        # To modify this behavior, you can inherit from common.OutputChecker in here
        # and overwrite the method `compare_files(generated_file, expected_file),
        # also see common.py.
        # common.OutputChecker(workdir / ".." /
        # "data" , expected_path , workdir).check()


if __name__ == "__main__":
    test_make_price_data()
