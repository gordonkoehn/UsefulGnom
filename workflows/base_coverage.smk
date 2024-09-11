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
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns


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
        mutations_of_interest = mutations_of_interest_dir,
        timeline = timeline_fp
    output:
        output_file = output_fp_total
    params:
        startdate = "2024-01-01",
        enddate = "2024-07-03",
        location = "Zürich (ZH)",
        # TODO: add protocol and subset params, see extract_sample_ID
    run:
        logging.info("Running total_coverage_depth")
        ug.analyze.run_total_coverage_depth(
            coverage_tsv_fps=total_coverage_dir,
            mutations_of_interest_fp=input.mutations_of_interest,
            timeline_file_dir=input.timeline,
            output_file=output.output_file,
            startdate = params.startdate,
            enddate = params.enddate,
            location = params.location
        )

rule mutation_statistics:
    """Compute mutation frequencies from the basecnt and general coverages and report the statistics
    """
    input:
        basecnt_coverage = output_fp_basecnt,
        total_coverage = output_fp_total
    params:
        location = {location},
        date = {date}
    output:
        heatmap = "/cluster/home/koehng/temp/mutstat/{location}/heatmapC23039G_G22599C_{location}_{date}.pdf",
        lineplot = "/cluster/home/koehng/temp/mutstat/{location}/lineplotC23039G_G22599C_{location}_{date}.pdf",
        frequency_data_matrix = "/cluster/home/koehng/temp/mutstat/{location}/frequency_data_matrix_{location}_{date}.csv",
        mutations_statistics = "/cluster/home/koehng/temp/mutstat/{location}/mutations_statistics_C23039G_G22599C_{location}_{date}.csv"
    run:
        logging.info("Running mutation_statistics")
        # Median frequency with IQR

        ## Labels for the plots
        location = params.location
        date = params.date

        # Compute mutation frequencies based on the

        basecnt_coverage_csv = input.basecnt_coverage
        total_cov = input.total_coverage

        basecnt = pd.read_csv(basecnt_coverage_csv, header=0, index_col=0)
        totalcnt = pd.read_csv(total_cov, header=0, index_col=0)
        # If position is covered less than 20 reads -> not enough information
        totalcnt[totalcnt < 20] = None
        # Computing mutations statistics:
        frequency_data_matrix = basecnt / totalcnt
        logging.info("Saving frequency data matrix")
        frequency_data_matrix.to_csv(
            output.frequency_data_matrix,
            header=True,
            index=True,
        )
        logging.info("Saved frequency data matrix")

        sns.set(rc={"figure.figsize": (8, 8)})
        samples = frequency_data_matrix.columns.to_list()
        # plot heatmap in normal scale
        df = frequency_data_matrix.transpose()
        sns.set_style("white")

        g = sns.heatmap(df, yticklabels=samples, cmap="Blues", linewidths=0, linecolor="none")

        fig = g.get_figure()
        plt.yticks(rotation=0, fontsize=8)
        # Set y-axis ticks and labels
        # Get the figure and axes
        ax = g.axes

        ax.set_xticks([x + 0.5 for x in range(df.shape[1])])
        ax.set_xticklabels(
            df.transpose().index, fontsize=8, rotation=0, ha="right", va="center"
        )
        logging.info("Saving heatmap")
        fig.savefig(
            output.heatmap,
            format="pdf",
            bbox_inches="tight",
        )
        logging.info("Saved heatmap")

        #####################################
        # LINE PLOT
        explanatory_labels = {
            "C23039G": "C23039G (KP.3)",
            "G22599C": "G22599C (KP.2)",
        }

        # Plot line plot
        sns.set(rc={"figure.figsize": (10, 5)})
        sns.set_style("white")

        # Transpose the DataFrame to have samples as columns
        df = frequency_data_matrix.transpose()

        # Create the line plot
        fig, ax = plt.subplots()

        # Plot each sample
        for sample in df.columns:
            explanatory_label = explanatory_labels.get(sample, sample)
            ax.plot(
                df.index, df[sample], label=explanatory_label, marker="o"
            )  # 'o' adds points to the line plot

        # Customize the plot
        plt.xticks(rotation=45, fontsize=6, ha="right")
        plt.yticks(fontsize=8)
        plt.xlabel("Day", fontsize=10)
        plt.ylabel("Frequency", fontsize=10)
        plt.title(f"Mutation frequencies {location}", fontsize=12)
        plt.legend(title="Mutations", loc="upper left")

        logging.info("Saving lineplot")
        # Save the figure
        fig.savefig(
            output.lineplot,
            format="pdf",
            bbox_inches="tight",
        )
        logging.info("Saved lineplot")


        #####################################
        # convert columns to date type
        frequency_data_matrix.columns = pd.to_datetime(frequency_data_matrix.columns)

        # the most recent date in the data matrix:
        most_recent_date = frequency_data_matrix.columns.max()

        # select most recent 2 weeks
        two_weeks_ago = most_recent_date - timedelta(weeks=2)
        mut_last_2_weeks = frequency_data_matrix.loc[
            :, frequency_data_matrix.columns >= two_weeks_ago
        ]
        medians = mut_last_2_weeks.median(axis=1)
        q1 = mut_last_2_weeks.quantile(0.25, axis=1)
        q3 = mut_last_2_weeks.quantile(0.75, axis=1)
        iqr = q3 - q1

        # Combine results into a DataFrame
        results_2_weeks = pd.DataFrame({"Median": medians, "IQR": iqr, "Q1": q1, "Q3": q3})

        # select most recent 6 weeks
        six_weeks_ago = most_recent_date - timedelta(weeks=6)
        mut_last_6_weeks = frequency_data_matrix.loc[
            :, frequency_data_matrix.columns >= six_weeks_ago
        ]
        medians = mut_last_6_weeks.median(axis=1)
        q1 = mut_last_6_weeks.quantile(0.25, axis=1)
        q3 = mut_last_6_weeks.quantile(0.75, axis=1)
        iqr = q3 - q1

        # Combine results into a DataFrame
        results_6_weeks = pd.DataFrame({"Median": medians, "IQR": iqr, "Q1": q1, "Q3": q3})

        # select most recent 12 weeks (3 months)
        three_months_ago = most_recent_date - timedelta(weeks=12)
        mut_last_3_months = frequency_data_matrix.loc[
            :, frequency_data_matrix.columns >= three_months_ago
        ]
        medians = mut_last_3_months.median(axis=1)
        q1 = mut_last_3_months.quantile(0.25, axis=1)
        q3 = mut_last_3_months.quantile(0.75, axis=1)
        iqr = q3 - q1

        # Combine results into a DataFrame
        results_12_weeks = pd.DataFrame({"Median": medians, "IQR": iqr, "Q1": q1, "Q3": q3})

        # select most recent 24 weeks (6 months)
        six_months_ago = most_recent_date - timedelta(weeks=24)
        mut_last_6_months = frequency_data_matrix.loc[
            :, frequency_data_matrix.columns >= six_months_ago
        ]
        medians = mut_last_6_months.median(axis=1)
        q1 = mut_last_6_months.quantile(0.25, axis=1)
        q3 = mut_last_6_months.quantile(0.75, axis=1)
        iqr = q3 - q1

        # Combine results into a DataFrame
        results_24_weeks = pd.DataFrame({"Median": medians, "IQR": iqr, "Q1": q1, "Q3": q3})

        # Combine information about each mutation into a single df
        dict_mut = {}
        for i, mutation in enumerate(frequency_data_matrix.index):
            dict_mut[f"df_mut_{mutation}"] = pd.concat(
                [
                    round(results_2_weeks.loc[mutation, :], 3),
                    round(results_6_weeks.loc[mutation, :], 3),
                    round(results_12_weeks.loc[mutation, :], 3),
                    round(results_24_weeks.loc[mutation, :], 3),
                ],
                keys=["2weeks", "6weeks", "12weeks", "24weeks"],
                axis=0,
            )
        combined_df = pd.concat(dict_mut, axis=0).reset_index()
        combined_df.columns = ["mutation", "time", "statistic", "value"]

        logging.info("Saving mutation statistics")
        combined_df.to_csv(
            output.mutations_statistics,
            header=True,
            index=False,
        )
        logging.info("Saved mutation statistics")


rule mutation_statistics_Zürich_2024_07_03:
    input:
        "/cluster/home/koehng/temp/mutstat/Zürich (ZH)/lineplotC23039G_G22599C_Zürich (ZH)_2024-07-03.pdf",