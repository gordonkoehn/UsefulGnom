"""Implements the relative amplicon coverage."""


configfile: "config/amplicon_cov.smk"


rule relative_amplicon_coverage_per_batch:
    """
    Calculate the relative amplicon coverage for all samples in the batch specific samples{batch}.tsv file.
    """
    input:
        sample_list=config["sample_list_dir"] + "samples{batch}.tsv",
        samples=config["sample_dir"],
    output:
        heatmap=config["output_dir"] + "{batch}/cov_heatmap.pdf",
    params:
        primers_fp=config["primers_fp"],
        output_dir=config["output_dir"] + "{batch}/",
    log:
        config["output_dir"] + "relative_amplicon_coverage_per_batch/{batch}.log",
    shell:
        """
        mkdir -p {params.output_dir}
        python scripts/amplicon_covs.py \
            -s {input.sample_list} \
            -f {input.samples} \
            -r {params.primers_fp} \
            -o {params.output_dir} \
            -p \
            -v 
        """


rule get_samples_per_batch:
    """
    Get the samples for the batch from the samples.tsv file and makes a new 
    batch specific list of samples in file samples{batch}.tsv
    """
    input:
        samples_list=config["sample_list_dir"] + "samples.tsv",
    output:
        samples_batch=config["sample_list_dir"] + "samples{batch}.tsv",
    log:
        config["output_dir"] + "get_samples_per_batch_{batch}.log",
    shell:
        """
        grep {wildcards.batch} {input.samples_list} > {output.samples_batch}
        """


rule get_coverage_for_batch:
    """
    Calculate the relative amplicon coverage for all samples in the batch specific samples{batch}.tsv file.
    """
    input:
        samples=f"{config['output_dir']}{config['batch']}/cov_heatmap.pdf",
