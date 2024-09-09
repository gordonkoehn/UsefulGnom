import logging
import glob

import usefulgnom as ug

from pathlib import Path


###################################
### Enrionmental Variables
# Inputs
basecnt_tsv_dir = "/cluster/project/pangolin/work-vp-test/results/*/*/alignments/basecnt.tsv.gz"
datamatrix_dir = "/cluster/home/koehng/temp/datamatrix.csv"
timeline_fp = "/cluster/project/pangolin/work-vp-test/variants/timeline.tsv"
# Outputs
output_fp = "/cluster/home/koehng/temp/coverage.csv"
###################################



rule basecnt_coverage_depth:
    """Generate matrix of coverage depth per base position
    """
    input:
        # basecnt_tsv = glob.glob(basecnt_tsv_dir, recursive=True),
        datamatrix = datamatrix_dir,
        timeline = timeline_fp
    output:
        output_file = output_fp
    run:
        logging.info("Running basecnt_coverage_depth")
        ug.analyze.run_basecnt_coverage(
            basecnt_fps=basecnt_tsv_dir,
            timeline_file_dir=input.timeline,
            datamatrix_dir=input.datamatrix,
            output_file=output.output_file
        )