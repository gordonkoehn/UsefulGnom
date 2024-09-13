import click
import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns


def get_samples_paths(main_samples_path, samplestsv):
    sam_paths_list = []
    with open(samplestsv, "r") as f:
        for line in f:
            tmp = line.rstrip("\n").split("\t")
            sam_paths_list.append(
                main_samples_path
                + "/"
                + tmp[0]
                + "/"
                + tmp[1]
                + "/alignments/coverage.tsv.gz"
            )
    return sam_paths_list


def load_bedfile(bed):
    bedfile = pd.read_table(bed, header=None)
    bedfile["sense"] = [re.search("(LEFT|RIGHT)", i).group(1) for i in bedfile[3]]
    bedfile["primer_num"] = [
        int(re.search("_([0-9]+)_", i).group(1)) for i in bedfile[3]
    ]
    bedfile["pool"] = [
        int(re.search("([1-2])$", i).group(1)) for i in bedfile[4].astype("str")
    ]
    bedfile = bedfile[[re.search("alt", i) is None for i in bedfile[3]]]
    return bedfile


def make_amplicons_df(bedfile):
    amplicons = []
    for i in np.unique(bedfile["primer_num"]):
        pr_num = i
        seq_start = bedfile[
            (bedfile["primer_num"] == pr_num) & (bedfile["sense"] == "LEFT")
        ][2].values[0]
        primer_start = bedfile[
            (bedfile["primer_num"] == pr_num) & (bedfile["sense"] == "LEFT")
        ][1].values[0]
        seq_end = bedfile[
            (bedfile["primer_num"] == pr_num) & (bedfile["sense"] == "RIGHT")
        ][1].values[0]
        primer_end = bedfile[
            (bedfile["primer_num"] == pr_num) & (bedfile["sense"] == "RIGHT")
        ][2].values[0]
        pool = bedfile[bedfile["primer_num"] == pr_num]["pool"].values[1]
        amplicons.append([pool, pr_num, primer_start, seq_start, seq_end, primer_end])

    amplicons_df = pd.DataFrame(
        np.array(amplicons),
        columns=[
            "pool",
            "primer_num",
            "primer_start",
            "seq_start",
            "seq_end",
            "primer_end",
        ],
    )

    q_starts = []
    q_stops = []
    for i in range(amplicons_df.shape[0]):
        if i > 0:
            query_start = amplicons_df.iloc[i - 1]["primer_end"] + 5
        else:
            query_start = amplicons_df.iloc[i]["primer_start"]
        if i < amplicons_df.shape[0] - 1:
            query_stop = amplicons_df.iloc[i + 1]["primer_start"] - 5
        else:
            query_stop = amplicons_df.iloc[i]["seq_end"]
        q_starts.append(query_start)
        q_stops.append(query_stop)
    amplicons_df["query_start"] = q_starts
    amplicons_df["query_end"] = q_stops
    return amplicons_df


def get_amplicon_cov(cov_df, start, stop, length=20):
    amplicon_slice = cov_df.iloc[np.r_[start:length, (stop - length) : stop], [2]]
    return np.median(amplicon_slice)


def get_count_reads(cov_df, amplicons_df):
    cov = amplicons_df.apply(
        lambda x: get_amplicon_cov(cov_df, x["query_start"], x["query_end"]), axis=1
    )
    return cov


def make_cov_heatmap(cov_df, output=None):
    plt.figure(figsize=(15, 8 * 2.5))
    split_at = round(cov_df.shape[0] / 2)
    plt.subplot(1, 2, 1)
    ax = sns.heatmap(
        cov_df.iloc[0:split_at, 1:],
        cmap="Reds",
        vmin=0,
        square=True,
        cbar_kws={"shrink": 0.2, "anchor": (0.0, 0.8)},
    )
    sns.heatmap(
        cov_df.iloc[0:split_at, 1:],
        cmap=plt.get_cmap("binary"),
        vmin=0,
        vmax=2,
        mask=cov_df.iloc[0:split_at, 1:] > 0,
        cbar=False,
        ax=ax,
    )
    plt.xlabel("amplicon")
    plt.ylabel("sample")
    plt.title("Samples 0:{}".format(split_at))
    plt.subplot(1, 2, 2)
    ax = sns.heatmap(
        cov_df.iloc[split_at:, 1:],
        cmap="Reds",
        vmin=0,
        square=True,
        cbar_kws={"shrink": 0.2, "anchor": (0.0, 0.8)},
    )
    sns.heatmap(
        cov_df.iloc[split_at:, 1:],
        cmap=plt.get_cmap("binary"),
        vmin=0,
        vmax=2,
        mask=cov_df.iloc[split_at:, 1:] > 0,
        cbar=False,
        ax=ax,
    )
    plt.xlabel("amplicon")
    plt.ylabel("sample")
    plt.title("Samples {}:{}".format(split_at, cov_df.shape[0] - 1))
    if output is not None:
        plt.savefig(output)


@click.command()
@click.option(
    "-r",
    "--bedfile-addr",
    required=True,
    type=click.Path(exists=True),
    help="Bedfile of the articV3 primers.",
)
@click.option(
    "-s",
    "--samp-file",
    default="/cluster/project/pangolin/working/samples.tsv",
    type=click.Path(exists=True),
    help="TSV file like samples.tsv.",
)
@click.option(
    "-f",
    "--samp-path",
    default="/cluster/project/pangolin/working/samples",
    type=click.Path(exists=True),
    help="Main path to samples.",
)
@click.option(
    "-o", "--outdir", default=os.getcwd(), type=click.Path(), help="Output directory."
)
@click.option("-p", "--makeplots", is_flag=True, help="Output plots.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
def main(bedfile_addr, samp_file, samp_path, outdir, makeplots, verbose):
    """
    Script to calculate primer rebalancings according to november 2020 version 5
    of the ARTIC V3 protocol for sars-cov-2 sequencing.
    """
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    if verbose:
        click.echo("Loading primers bedfile.")
    amplicons_df = make_amplicons_df(load_bedfile(bedfile_addr))

    if verbose:
        click.echo("Reading list of coverage files.")
    sam_list = get_samples_paths(samp_path, samp_file)

    if verbose:
        click.echo("Loading and parsing coverage files.")
    all_covs = []
    indexes = []
    with click.progressbar(sam_list, label="Parsing coverage files") as bar:
        for sam in bar:
            try:
                temp_cov_df = pd.read_csv(sam, sep="\t", compression="gzip")
                temp_frac_read_df = pd.DataFrame(
                    get_count_reads(temp_cov_df, amplicons_df)
                ).T
                indexes.append(sam.split("/")[-4])
                all_covs.append(temp_frac_read_df)
            except FileNotFoundError:
                if verbose:
                    click.echo(f"WARNING: file {sam} not found.")

    all_covs = pd.concat(all_covs, axis=0)
    all_covs = all_covs.reset_index(drop=True)
    all_covs_frac = all_covs.div(all_covs.sum(axis=1), axis=0)

    all_covs = pd.concat(
        [pd.DataFrame({"sample": indexes}), all_covs.reset_index(drop=True)],
        axis=1,
        ignore_index=False,
    )
    all_covs_frac = pd.concat(
        [pd.DataFrame({"sample": indexes}), all_covs_frac.reset_index(drop=True)],
        axis=1,
        ignore_index=False,
    )

    if verbose:
        click.echo("Outputting .csv's")
    all_covs.to_csv(os.path.join(outdir, "amplicons_coverages.csv"), index=False)
    all_covs_frac.to_csv(
        os.path.join(outdir, "amplicons_coverages_norm.csv"), index=False
    )

    if makeplots:
        if verbose:
            click.echo("Outputting plots.")
        make_cov_heatmap(all_covs, os.path.join(outdir, "cov_heatmap.pdf"))


if __name__ == "__main__":
    main()
