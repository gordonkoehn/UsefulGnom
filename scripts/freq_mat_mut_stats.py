# Compute mutation frequencies from the basecnt and general coverages and report the statistics
# Median frequency with IQR
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Compute mutation frequencies based on the
# def read_csv(basecnt_coverage_csv, general_coverage_csv):

# Change location name (WWTP)
location = "zurich"
date = "07_03"

basecnt_coverage_csv = f"/Users/arimaite/Documents/GitHub/SARS_CoV_2_variants/analysis_2024_KP.2_KP.3/statistic_KP_over_time/{location}/mut_base_coverage_{location}_{date}.csv"
total_cov = f"/Users/arimaite/Documents/GitHub/SARS_CoV_2_variants/analysis_2024_KP.2_KP.3/statistic_KP_over_time/{location}/mut_total_coverage_{location}_{date}.csv"

basecnt = pd.read_csv(basecnt_coverage_csv, header=0, index_col=0)
totalcnt = pd.read_csv(total_cov, header=0, index_col=0)
# If position is covered less than 20 reads -> not enough information
totalcnt[totalcnt < 20] = None
# Computing mutations statistics:
frequency_data_matrix = basecnt / totalcnt
frequency_data_matrix.to_csv(
    f"/Users/arimaite/Documents/GitHub/SARS_CoV_2_variants/analysis_2024_KP.2_KP.3/statistic_KP_over_time/{location}/frequency_data_matrix_kp3_{location}_{date}.csv",
    header=True,
    index=True,
)

# frequency_data_matrix.fillna(0, inplace=True)
# print(frequency_data_matrix)

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


fig.savefig(
    f"/Users/arimaite/Documents/GitHub/SARS_CoV_2_variants/analysis_2024_KP.2_KP.3/statistic_KP_over_time/{location}/heatmapC23039G_G22599C_{location}_{date}.pdf",
    format="pdf",
    bbox_inches="tight",
)

# plt.show()
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

# Save the figure
fig.savefig(
    f"/Users/arimaite/Documents/GitHub/SARS_CoV_2_variants/analysis_2024_KP.2_KP.3/statistic_KP_over_time/{location}/lineplotC23039G_G22599C_{location}_{date}.pdf",
    format="pdf",
    bbox_inches="tight",
)

# Show the plot
# plt.show()
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

print(combined_df)
combined_df.to_csv(
    f"/Users/arimaite/Documents/GitHub/SARS_CoV_2_variants/analysis_2024_KP.2_KP.3/statistic_KP_over_time/{location}/mutations_statistics_C23039G_G22599C_{location}_{date}.csv",
    header=True,
    index=False,
)
