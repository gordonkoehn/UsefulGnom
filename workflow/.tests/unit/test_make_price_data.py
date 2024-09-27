"""
Test of make_price_data rule

This is a mock test trying to understand how one can test snakmake rules.
"""

import os
import sys
import subprocess as sp
from tempfile import TemporaryDirectory
import shutil
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))


def test_make_price_data():
    """
    Test the make_price_data rule.

    Check if the rule generates the expected output.
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
            "workflow/.tests/unit/smk_testing/data/AMZN_2012-06-21_34200000_57600000_message_1.csv"
        )
        expected_path = Path("workflow/.tests/unit/smk_testing/expected")
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
        result = sp.run(
            [
                "diff",
                str(workdir / "results" / "statistics.csv"),
                str(expected_path / "statistics.csv"),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Files are different:\n{result.stdout}"


### Main
if __name__ == "__main__":
    try:
        test_make_price_data()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
