"""Implements the relative amplicon coverage."""


##################################################
### Environment
##################################################
output_dir = "/cluster/home/koehng/temp/amplicon_cov/20210122out/"
##################################################


rule relative_amplicon_coverage:
    input:
        sample_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples.tsv",
        samples = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples"
    output:
        heatmap = output_dir + "cov_heatmap.pdf"
    params:
        primers_fp ="../resources/amplicon_cov/articV3primers.bed",
        output_dir = output_dir
    shell:
        """
        mkdir -p {params.output_dir}
        python ../scripts/amplicon_covs.py \
            -s {input.sample_list} \
            -f {input.samples} \
            -r {params.primers_fp} \
            -o {params.output_dir}
        """