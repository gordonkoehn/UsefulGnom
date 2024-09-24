"""Implements the relative amplicon coverage."""


configfile: "../config/amplicon_cov.smk"


rule relative_amplicon_coverage_per_batch:
    """
    Calculate the relative amplicon coverage for all samples in the batch specific samples{batch}.tsv file.
    """
    input:
        sample_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples{batch}.tsv",
        samples = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples"
    output:
        heatmap = config["output_dir"] + "{batch}/cov_heatmap.pdf",
    params:
        primers_fp ="../resources/amplicon_cov/articV3primers.bed",
        output_dir = config["output_dir"] + "{batch}/"
    log:
        config["output_dir"] + "relative_amplicon_coverage_per_batch/{batch}.log"
    shell:
        """
        mkdir -p {params.output_dir}
        python ../scripts/amplicon_covs.py \
            -s {input.sample_list} \
            -f {input.samples} \
            -r {params.primers_fp} \
            -o {params.output_dir} \
            -p \
            -v 
        """


rule get_samples_per_batch:
    input:
        samples_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples.tsv"
    output:
        samples_batch = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples{batch}.tsv"
    log:
        config["output_dir"] + "get_samples_per_batch_{batch}.log"
    shell:
        """
        grep {wildcards.batch} {input.samples_list} > {output.samples_batch}
        """

rule get_coverage_for_batch:
    """
    Calculate the relative amplicon coverage for all samples in the batch specific samples{batch}.tsv file.
    """
    input:
        samples = f"{config['output_dir']}20240705_AAFH52MM5/cov_heatmap.pdf",