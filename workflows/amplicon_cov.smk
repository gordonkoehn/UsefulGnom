"""Implements the relative amplicon coverage."""


##################################################
### Environment
##################################################
output_dir = "/cluster/home/koehng/temp/amplicon_cov/20210122out/"
primers_fp = "../resources/amplicon_cov/articV3primers.bed"
##################################################


rule relative_amplicon_coverage:
    input:
        sample_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples.tsv",
        samples = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples",
    output:
        output_dir = output_dir+ "/cov_heatmap.pdf"
    shell:
        f"""
        python ../scripts/amplicon_covs.py -pv /
            -s {{input.sample_list}} /
            -f {{input.samples}} /
            -r articV3primers.bed /
            -o {{output.output_dir}} /
        """