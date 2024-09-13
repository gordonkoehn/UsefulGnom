"""Implements the relative amplicon coverage."""


##################################################
### Environment
##################################################
output_dir = "/cluster/home/koehng/temp/amplicon_cov/click/"
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
        python ../scripts/amplicon_covs_click.py \
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
        heatmap = output_dir + "{batch}/cov_heatmap.pdf",
        median_cov_hist = output_dir + "{batch}/median_cov_hist.pdf",
        make_median_coverage_barplot = output_dir + "{batch}/make_median_coverage_barplot.pdf",
        cov_heatmap_norm = output_dir + "{batch}/cov_heatmap_norm.pdf",
        median_cov_hist_norm = output_dir + "{batch}/median_cov_hist_norm.pdf",
        median_coverage_barplot_norm = output_dir + "{batch}/median_coverage_barplot_norm.pdf"
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
    input:
        samples_list = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples.tsv"
    output:
        samples_batch = "/cluster/project/pangolin/work-amplicon-coverage/test_data/samples{batch}.tsv"
    shell:
        """
        grep {wildcards.batch} {input.samples_list} > {output.samples_batch}
        """

rule get_coverage_for_batch:
    """
    Calculate the relative amplicon coverage for all samples in the batch specific samples{batch}.tsv file.
    """
    input:
        samples = f"{output_dir}20240705_AAFH52MM5/cov_heatmap.pdf",
        median_cov_hist = output_dir + "{batch}/median_cov_hist.pdf",
        make_median_coverage_barplot = output_dir + "{batch}/make_median_coverage_barplot.pdf",
        cov_heatmap_norm = output_dir + "{batch}/cov_heatmap_norm.pdf",
        median_cov_hist_norm = output_dir + "{batch}/median_cov_hist_norm.pdf",
        median_coverage_barplot_norm = output_dir + "{batch}/median_coverage_barplot_norm.pdf"