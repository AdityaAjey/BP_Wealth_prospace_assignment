# BP_Wealth_prospace_assignment
This is the assignment for BP Wealth: Generating Alphas For Global Markets project which I came to know through prospace. The code can be run when the dataset
asset_1.csv is put in same folder as the code. The code does the following tasks:

Task 1: Static Thresholds
Build a trading strategy based on static thresholds for building and liquidating a position. Assume that you can, at maximum, hold 1 unit of the stock in either the buy or sell side. At the end of the cycle, assume you have to liquidate your position completely. Assume no transaction costs. Record your trades by adding a column called position to the asset file, with a value of 1, 0 or -1 denoting the position you hold at that time.

Let’s say the build threshold is 0.6 and liquidate threshold is 0.2. When the alpha goes from 0.5 to 0.8, you build a position of 1 unit, buying 1 stock. When the alpha goes from 0.8 to 0.4, you do nothing. When the alpha goes from 0.4 to 0.1, you liquidate your position, now holding 0 units. When the alpha goes from 0.1 to -0.5, you do nothing. When the alpha goes from -0.5 to -1.2, you build a negative position, shorting the stock and holding -1 stocks. When the alpha goes from -1.2 to -1, you do nothing. When the alpha goes from -1 to 0, you liquidate your position, holding 0 stocks.

Task 2: Backtesting Engine
Build an engine that can generate the P&L statement basis your trading strategy file.

Task 3: Optimizing Thresholds
Find optimal thresholds for your alpha, maximising PnL for the given data.

