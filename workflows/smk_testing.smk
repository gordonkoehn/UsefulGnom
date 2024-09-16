

	    # 1.) Time: 		
		# 		Seconds after midnight with decimal 
		# 		precision of at least milliseconds 
		# 		and up to nanoseconds depending on 
		# 		the requested period
	    # 2.) Type:
		# 		1: Submission of a new limit order
		# 		2: Cancellation (Partial deletion 
		# 		   of a limit order)
		# 		3: Deletion (Total deletion of a limit order)
		# 		4: Execution of a visible limit order			   	 
		# 		5: Execution of a hidden limit order
		# 		7: Trading halt indicator 				   
		# 		   (Detailed information below)
	    # 3.) Order ID: 	
		# 		Unique order reference number 
		# 		(Assigned in order flow)
	    # 4.) Size: 		
		# 		Number of shares
	    # 5.) Price: 		
		# 		Dollar price times 10000 
		# 		(i.e., A stock price of $91.14 is given 
		# 		by 911400)
	    # 6.) Direction:
		# 		-1: Sell limit order
		# 		1: Buy limit order
				
		# 		Note: 
		# 		Execution of a sell (buy) limit
		# 		order corresponds to a buyer (seller) 
		# 		initiated trade, i.e. Buy (Sell) trade.


rule make_price_data:
    input:
        orderbook = "../data/AMZN_2012-06-21_34200000_57600000_orderbook_1.csv"
    output:
        statistics = "../data/statistics.csv"
    run:
        import pandas as pd 
        # Read the data
        data = pd.read_csv(orderbook, header=None)
        # asign the columns
        data.columns = ["Time", "Type", "Order ID", "Size", "Price", "Direction"]
        # get start time and end time of the data
        start_time = data["Time"].min()
        end_time = data["Time"].max()
        # choose bounds for the intervals
        bounds = range(start_time, end_time, 300000)
        # calculate statitiscs, mean, std, min, max for each column in intervals of 5 minutes
        statistics = data.groupby(pd.cut(data["Time"], bins=bounds)).agg(["mean", "std", "min", "max"])
        # save the statistics
        statistics.to_csv(output.statistics, index=False)