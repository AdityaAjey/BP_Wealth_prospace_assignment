import pandas as pd
import numpy as np
from itertools import product
from multiprocessing import Pool, cpu_count
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the dataset
df = pd.read_csv('./asset_1.csv')

class TradingStrategy:
    def __init__(self, build_threshold=0.6, liquidate_threshold=0.2, short_build_threshold=-0.6, short_liquidate_threshold=-0.2):
        self.build_threshold = build_threshold
        self.liquidate_threshold = liquidate_threshold
        self.short_build_threshold = short_build_threshold
        self.short_liquidate_threshold = short_liquidate_threshold
    
    def apply_static_thresholds(self, df):
        df['position'] = 0  # Initialize positions to 0
        df['trade'] = 0  # Initialize trade column to 0
        current_position = 0

        for i in range(1, len(df)):
            alpha = df.at[i, 'alpha']
            prev_alpha = df.at[i-1, 'alpha']
            
            if current_position == 0:
                if alpha >= self.build_threshold and prev_alpha < self.build_threshold:
                    current_position = 1
                    df.at[i, 'trade'] = 1  # Buy
                elif alpha <= self.short_build_threshold and prev_alpha > self.short_build_threshold:
                    current_position = -1
                    df.at[i, 'trade'] = -1  # Short
            elif current_position == 1:
                if alpha <= self.liquidate_threshold and prev_alpha > self.liquidate_threshold:
                    current_position = 0
                    df.at[i, 'trade'] = -1  # Sell
            elif current_position == -1:
                if alpha >= self.short_liquidate_threshold and prev_alpha < self.short_liquidate_threshold:
                    current_position = 0
                    df.at[i, 'trade'] = 1  # Cover

            df.at[i, 'position'] = current_position

        # Liquidate any remaining positions at the end
        if current_position == 1:
            df.at[len(df) - 1, 'trade'] = -1
        elif current_position == -1:
            df.at[len(df) - 1, 'trade'] = 1
        
        df.at[len(df) - 1, 'position'] = 0

        return df

class BacktestingEngine:
    def __init__(self, df):
        self.df = df
    
    def calculate_pnl(self):
        self.df['pnl'] = 0  # Initialize P&L to 0
        self.df['cashflow'] = 0  # Initialize cashflow to 0
        
        for i in range(1, len(self.df)):
            prev_position = self.df.at[i-1, 'position']
            position = self.df.at[i, 'position']
            trade = self.df.at[i, 'trade']

            if trade == 1:  # Buy
                self.df.at[i, 'cashflow'] = -self.df.at[i, 'price']
            elif trade == -1:  # Sell
                self.df.at[i, 'cashflow'] = self.df.at[i, 'price']

            if prev_position == 1:
                self.df.at[i, 'pnl'] = self.df.at[i, 'price'] - self.df.at[i-1, 'price']
            elif prev_position == -1:
                self.df.at[i, 'pnl'] = self.df.at[i-1, 'price'] - self.df.at[i, 'price']
        
        total_pnl = self.df['pnl'].sum() + self.df['cashflow'].sum()
        return total_pnl, self.df

def optimize_thresholds(args):
    df, build_range, liquidate_range, short_build_range, short_liquidate_range = args
    best_pnl = -np.inf
    best_thresholds = (0, 0, 0, 0)
    
    for thresholds in product(build_range, liquidate_range, short_build_range, short_liquidate_range):
        strategy = TradingStrategy(*thresholds)
        df_temp = strategy.apply_static_thresholds(df.copy())
        backtester = BacktestingEngine(df_temp)
        pnl, _ = backtester.calculate_pnl()
        if pnl > best_pnl:
            best_pnl = pnl
            best_thresholds = thresholds
            
    return best_thresholds, best_pnl

def main():
    # Define ranges for thresholds
    build_range = np.linspace(0.4, 0.8, 5)
    liquidate_range = np.linspace(0.1, 0.3, 5)
    short_build_range = np.linspace(-0.4, -0.8, 5)
    short_liquidate_range = np.linspace(-0.1, -0.3, 5)

    # Optimize thresholds
    pool = Pool(cpu_count())
    args = (df, build_range, liquidate_range, short_build_range, short_liquidate_range)
    results = pool.map(optimize_thresholds, [args])
    pool.close()
    pool.join()

    optimal_thresholds, optimal_pnl = max(results, key=lambda x: x[1])

    logging.info(f"Optimal Thresholds: {optimal_thresholds}")
    logging.info(f"Optimal PnL: {optimal_pnl}")

    # Apply optimal thresholds to the dataset
    strategy = TradingStrategy(*optimal_thresholds)
    df_with_positions = strategy.apply_static_thresholds(df)
    backtester = BacktestingEngine(df_with_positions)
    total_pnl, df_with_pnl = backtester.calculate_pnl()

    logging.info(f"Total PnL with optimal thresholds: {total_pnl}")
    logging.info(df_with_pnl.head(10))

    # Save the dataset with positions and PnL
    df_with_pnl.to_csv('./asset_1_with_positions_and_pnl.csv', index=False)

    # Plot results (disabled due to OpenGL errors)
    # plt.figure(figsize=(12, 6))
    # plt.plot(df_with_pnl['price'], label='Price')
    # plt.plot(df_with_pnl['pnl'].cumsum(), label='Cumulative PnL')
    # plt.legend()
    # plt.title('Price and Cumulative PnL Over Time')
    # plt.show()

if __name__ == "__main__":
    main()

