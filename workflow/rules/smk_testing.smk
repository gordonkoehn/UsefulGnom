
import pandas as pd 
from datetime import datetime, timedelta


configfile: "config/smk_testing_config.yaml"

rule make_price_data:
    input:
        orderbook = config["orderbook"]
    output:
        statistics = config["statistics"]
    run:
        # Read the data
        data = pd.read_csv(input.orderbook)
        # assign the columns
        data.columns = ["Time", "Type", "Order ID", "Size", "Price", "Direction"]
        # get start time and end time of the data
        start_time = data["Time"].min()
        end_time = data["Time"].max()
        # choose bounds for the intervals in seconds for 5-minute intervals
        bounds = range(int(start_time), int(end_time) + 1, 300)  # 300 seconds = 5 minutes
        statistics = data.groupby(pd.cut(data["Time"], bins=bounds)).agg(["mean", "std", "min", "max"])

        # add an intential error here for debugging
        # Set the "Price" column's "mean" value to -999
        # statistics.loc[:, ("Price", "mean")] = -999

        # save the statistics
        statistics.to_csv(output.statistics, index=False)