"""
This script tests the make_price_data rule.
"""

import os
import sys
import subprocess as sp
from tempfile import TemporaryDirectory
import shutil
from pathlib import Path

from common import compare_csv_files

sys.path.insert(0, os.path.dirname(__file__))


def test_make_price_data():
    """
    Test the make_price_data rule.
    """
    with TemporaryDirectory() as tmpdir:
        workdir = Path(tmpdir) / "workdir"
        workdir.mkdir(exist_ok=True)

        # Create necessary subdirectories
        (workdir / "config").mkdir(exist_ok=True)
        (workdir / "data").mkdir(exist_ok=True)
        (workdir / "results").mkdir(exist_ok=True)

        # Define paths
        mock_data_path = Path(
            "workflow/.tests/unit/make_price_data/data/AMZN_2012-06-21_34200000_57600000_message_1.csv"
        )
        expected_path = Path("workflow/.tests/unit/make_price_data/expected")
        config_path = Path("config/smk_testing_config.yaml")

        # Copy config to the temporary workdir
        shutil.copy(config_path, workdir / "config" / "smk_testing_config.yaml")

        # Copy mock data to the temporary workdir
        shutil.copy(mock_data_path, workdir / "data" / mock_data_path.name)

        # Run the test job

        sp.check_output(
            [
                "snakemake",
                "--snakefile",
                "workflow/rules/smk_testing.smk",
                "--configfile",
                str(workdir / "config" / "smk_testing_config.yaml"),
                "--config",
                f"orderbook={workdir}/data/AMZN_2012-06-21_34200000_57600000_message_1.csv",
                f"statistics={workdir}/results/statistics.csv",
                "--directory",
                str(workdir),
                "--cores",
                "1",
                "--forceall",
            ]
        )

        # Check the output
        assert (workdir / "results" / "statistics.csv").exists()

        # Compare output with expected result
        files_match = compare_csv_files(
            str(workdir / "results" / "statistics.csv"),
            str(expected_path / "statistics.csv"),
        )

        assert files_match, "Files are different within the specified tolerance"


### Main
if __name__ == "__main__":
    test_make_price_data()
    print("Test passed!")
