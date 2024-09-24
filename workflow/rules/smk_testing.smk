import pandas as pd 
import logging
from datetime import datetime, timedelta

# Use the specific config file for this test
configfile: "../config/smk_testing_config.yaml"

rule make_price_data:
    input:
        orderbook = config["orderbook"]
    output:
        statistics = config["statistics"]
    params:
        interval = config["interval"]
    run:
        # Read the data
        data = pd.read_csv(input.orderbook)
        # assign the columns
        data.columns = ["Time", "Type", "Order ID", "Size", "Price", "Direction"]
        # get start time and end time of the data
        start_time = data["Time"].min()
        end_time = data["Time"].max()
        # choose bounds for the intervals in seconds based on the config
        interval_seconds = params.interval * 60  # convert minutes to seconds
        bounds = range(int(start_time), int(end_time) + 1, interval_seconds)
        statistics = data.groupby(pd.cut(data["Time"], bins=bounds)).agg(["mean", "std", "min", "max"])

        # save the statistics
        statistics.to_csv(output.statistics, index=False)