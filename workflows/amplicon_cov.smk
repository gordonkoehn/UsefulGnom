"""Implements the relative amplicon coverage."""


##################################################
### Environment
##################################################
output_dir = "/cluster/home/koehng/temp/amplicon_cov/"
##################################################




rule relative_amplicon_coverage_allbatches:
    """
    Calculate the relative amplicon coverage for all samples in the samples.tsv file.
    """
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
            -o {params.output_dir} \
            -p 
        """


rule relative_amplicon_coverage_per_batch:
    """
    Calculate the relative amplicon coverage for all samples in the batch specific samples{batch}.tsv file.
    """
    input:
        sample_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples{batch}.tsv",
        samples = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples"
    output:
        heatmap = output_dir + "{batch}/cov_heatmap.pdf"
    params:
        primers_fp ="../resources/amplicon_cov/articV3primers.bed",
        output_dir = output_dir + "{batch}/"
    shell:
        """
        mkdir -p {params.output_dir}
        python ../scripts/amplicon_covs.py \
            -s {input.sample_list} \
            -f {input.samples} \
            -r {params.primers_fp} \
            -o {params.output_dir} \
            -p 
        """


rule get_samples_per_batch:
    params:
        # TODO: make this a config to be passed to the workflow viw the command line
        batch = "20210122_HY53JDRXX"
    input:
        samples_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples.tsv"
    output:
        samples_batch = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples{params.batch}.tsv"
    shell:
        """
        grep {params.batch} {input.samples_list} > {output.samples_batch}
        """
