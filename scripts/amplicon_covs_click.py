"""
Compute per amplicon relative coverage for a batch of samples.

It outputs a .csv with samples in the rows, first column is sample name and 
98 other columns are amplicons.  It needs a bedfile of primers, a .tsv to list 
the samples (like `/cluster/project/pangolin/working/samples.tsv`) and a 
directory where to find the aligned samples 
(like `/cluster/project/pangolin/working/samples/`).  
Optionally outputs plots.

Bedfile primers may be found at: eg. from: 
https://raw.githubusercontent.com/artic-network/artic-ncov2019/master/
primer_schemes/nCoV-2019/V3/nCoV-2019.bed

Usage:
If we want to analyze coverage of samples in batch HY53JDRXX,
with primers info in 'articV3primers.bed', we first need to create a tsv 
list of samples:

```grep 20210122_HY53JDRXX /cluster/project/pangolin/working/samples.tsv \
    > samples20210122_HY53JDRXX.tsv```

Then to compute coverages while plotting and with verbose, outputting into \
    'samples20210122_HY53JDRXX' directory:

```python ./amplicon_covs.py -pv -s samples20210122_HY53JDRXX.tsv \
    -r articV3primers.bed -o samples20210122_HY53JDRXX/```
                        
"""

import click
import numpy as np
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

from typing import Optional


def get_samples_paths(main_samples_path: Path, samplestsv):
    """Get list of paths to coverage files given from a samples.tsv list file."""
    main_samples_path_str = str(main_samples_path)
    sam_paths_list = []
    with open(samplestsv, "r") as f:
        for line in f:
            tmp = line.rstrip("\n").split("\t")
            sam_paths_list.append(
                main_samples_path_str
                + "/"
                + tmp[0]
                + "/"
                + tmp[1]
                + "/alignments/coverage.tsv.gz"
            )
    return sam_paths_list


def safe_regex_search(pattern: str, text: str, group: int = 1) -> Optional[str]:
    """Safely apply regex search and return group or None if not found."""
    match = re.search(pattern, text)
    return match.group(group) if match else None


def load_bedfile(bed: Path) -> pd.DataFrame:
    """Load bedfile and parse it."""
    bedfile = pd.read_table(bed, header=None)

    # Apply regex operations
    bedfile["sense"] = bedfile[3].apply(lambda x: safe_regex_search("(LEFT|RIGHT)", x))
    bedfile["primer_num"] = (
        bedfile[3].apply(lambda x: safe_regex_search("_([0-9]+)_", x)).astype(float)
    )
    bedfile["pool"] = (
        bedfile[4]
        .astype(str)
        .apply(lambda x: safe_regex_search("([1-2])$", x))
        .astype(float)
    )

    # Filter rows where 'alt' is not in column 3
    bedfile = bedfile[bedfile[3].apply(lambda x: "alt" not in str(x))]

    return bedfile


def make_amplicons_df(bedfile):
    """From primer info in bedfile create a dataframe with amplicon info."""
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
    """Get median coverage of an amplicon."""
    amplicon_slice = cov_df.iloc[np.r_[start:length, (stop - length) : stop], [2]]
    return np.median(amplicon_slice)


def get_count_reads(cov_df, amplicons_df):
    """Get coverage of all amplicons. ???"""
    cov = amplicons_df.apply(
        lambda x: get_amplicon_cov(cov_df, x["query_start"], x["query_end"]), axis=1
    )
    return cov


def make_cov_heatmap(cov_df, output=None):
    """Make heatmap of coverage."""
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
        click.echo(f"Saved heatmap to {output}")


def make_median_cov_hist(cov_df, output=None):
    """Make histogram of median coverage."""
    click.echo("Computing median coverage histogram")
    median = np.nanmedian(cov_df.iloc[:, 1:].values, axis=0)

    plt.figure(figsize=(12, 6))
    sns.histplot(y=median, binwidth=0.002, stat="density")
    plt.title("Median coverage histogram")
    plt.ylabel("median fraction of reads aligned on amplicon")
    plt.xlabel("density")
    plt.axhline(1 / 98, linestyle="--", color="black")

    if output is not None:
        plt.savefig(output)
        click.echo(f"Saved histogram to {output}")


def make_median_coverage_barplot(cov_df, output=None):
    """Make barplot of median coverage."""
    cov_df_long = pd.melt(cov_df.iloc[:, 1:])
    cov_df_long["pool"] = cov_df_long["variable"].astype("int").mod(2) + 1

    plt.figure(figsize=(22, 9))
    sns.barplot(
        x="variable", y="value", hue="pool", data=cov_df_long, estimator=np.median
    )
    plt.axhline(1 / 98, linestyle="--", color="black")
    plt.xlabel("amplicon")
    plt.ylabel("median fraction of reads")
    plt.title("Median coverage barplot")

    if output is not None:
        plt.savefig(output)
        click.echo(f"Saved median coverage barplot to {output}")


@click.command()
@click.option(
    "-r",
    "--bedfile-addr",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="Bedfile of the articV3 primers.",
)
@click.option(
    "-s",
    "--samp-file",
    default="/cluster/project/pangolin/working/samples.tsv",
    type=click.Path(exists=True, path_type=Path),
    help="TSV file like samples.tsv.",
)
@click.option(
    "-f",
    "--samp-path",
    default="/cluster/project/pangolin/working/samples",
    type=click.Path(exists=True, path_type=Path),
    help="Main path to samples.",
)
@click.option(
    "-o",
    "--outdir",
    default=os.getcwd(),
    type=click.Path(exists=True, path_type=Path),
    help="Output directory.",
)
@click.option("-p", "--makeplots", is_flag=True, help="Output plots.")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output.")
def main(
    bedfile_addr: Path,
    samp_file: Path,
    samp_path: Path,
    outdir: Path,
    makeplots,
    verbose,
):
    """
    Compute per amplicon relative coverage for a batch of samples.
    """
    outdir = Path(outdir)  # Ensure outdir is a Path object
    if not outdir.exists():
        outdir.mkdir(parents=True, exist_ok=True)

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

        try:
            make_median_cov_hist(all_covs, os.path.join(outdir, "median_cov_hist.pdf"))
        except Exception as e:
            click.echo(f"Error generating median_cov_hist plot: {str(e)}")

        try:
            make_median_coverage_barplot(
                all_covs, os.path.join(outdir, "median_coverage_barplot.pdf")
            )
        except Exception as e:
            click.echo(f"Error generating median_coverage_barplot plot: {str(e)}")

        try:
            make_cov_heatmap(
                all_covs_frac, os.path.join(outdir, "cov_heatmap_norm.pdf")
            )
        except Exception as e:
            click.echo(f"Error generating cov_heatmap_norm plot: {str(e)}")

        try:
            make_median_cov_hist(
                all_covs_frac, os.path.join(outdir, "median_cov_hist_norm.pdf")
            )
        except Exception as e:
            click.echo(f"Error generating median_cov_hist_norm plot: {str(e)}")

        try:
            make_median_coverage_barplot(
                all_covs_frac, os.path.join(outdir, "median_coverage_barplot_norm.pdf")
            )
        except Exception as e:
            click.echo(f"Error generating median_coverage_barplot_norm plot: {str(e)}")


if __name__ == "__main__":
    main()
