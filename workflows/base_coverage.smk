"""Implements 
    1) calculating basecnt coverage depth >> rule basecnt_coverage_depth,
    2) total coverage depth and 
    3) computing frequency matrix + calculating mutations statistics.

    Credits:
        - core code: @AugusteRi (arimaite@ethz.ch)
        - implementation: @koehng (koehng@ethz.ch)
"""

import logging
import glob

import usefulgnom as ug

from pathlib import Path


###################################
###### Enrionmental Variables
#### Inputs
# str - path pattern to basecnt.tsv files
basecnt_tsv_dir = "/cluster/project/pangolin/work-vp-test/results/*/*/alignments/basecnt.tsv.gz"
total_coverage_dir = "/cluster/project/pangolin/work-vp-test/results/*/*/alignments/coverage.tsv.gz"
### files
# singe file with colum [mut] listing mutation of interest in each row
mutations_of_interest_dir = "/cluster/home/koehng/temp/mutations_of_interest.csv"
# timeline file of columns [sample, batch, reads, proto, location_code, date, location]
timeline_fp = "/cluster/project/pangolin/work-vp-test/variants/timeline.tsv"
#### Outputs
# for basecnt_coverage_depth
output_fp_basecnt = "/cluster/home/koehng/temp/basecnt_coverage.csv"
# for total_coverage_depth
output_fp_total = "/cluster/home/koehng/temp/total_coverage.csv"
###################################



rule basecnt_coverage_depth:
    """Generate matrix of coverage depth per base position
    """
    input:
        mutations_of_interest = mutations_of_interest_dir,
        timeline = timeline_fp
    output:
        output_file = output_fp_basecnt
    params:
        startdate = "2024-01-01",
        enddate = "2024-07-03",
        location = "Zürich (ZH)",
        # TODO: add protocol and subset params, see extract_sample_ID
    run:
        logging.info("Running basecnt_coverage_depth")
        ug.analyze.run_basecnt_coverage(
            basecnt_fps=basecnt_tsv_dir,
            timeline_file_dir=input.timeline,
            mutations_of_interest_dir=input.mutations_of_interest,
            output_file=output.output_file,
            startdate = params.startdate,
            enddate = params.enddate,
            location = params.location
        )


rule total_coverage_depth:
    """ Calcultate the total coverage depth
    """ 
    input:
        coverage_tsv_dir = total_coverage_dir,
        timeline = timeline_fp
    output:
        output_file = output_fp_total
    run:
        logging.info("Running total_coverage_depth")
        ug.analyze.run_total_coverage_depth(
            coverage_tsv_dir=input.coverage_tsv_dir,
            timeline_file_dir=input.timeline,
            output_file=output.output_file
        )