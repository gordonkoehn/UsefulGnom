import logging

import usefulgnom as ug

from pathlib import Path


###################################
### Enrionmental Variables
# Inputs
basecnt_tsv_dir = "/cluster/project/pangolin/work-vp-test/results/{variant}/{batch}/alignments/basecnt.tsv.gz"
datamatrix_dir = "/cluster/project/pangolin/work-vp-test/results/{variant}/{batch}/alignments/coverage.tsv.gz"
timeline_fp = "/cluster/project/pangolin/work-vp-test/variants/timeline.tsv"
# Outputs
output_fp = "/cluster/home/koehng/temp/coverage.csv"
###################################



rule basecnt_coverage_depth:
    """Generate matrix of coverage depth per base position
    """
    input:
        basecnt_tsv = basecnt_tsv_dir,
        datamatrix = datamatrix_dir,
        timeline = timeline_fp
    output:
        output_file = output_fp
    run:
        logging.info("Running basecnt_coverage_depth")
        ug.analyse.basecnt_coverage(
            Path("data/coverage/coverage.tsv"),
            Path("data/coverage/coverage_depth.tsv"),
        )