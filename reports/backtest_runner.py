# Local verification runner using yfinance hourly data (DEV ONLY).
# Downloads hourly data for BTC-USD and ETH-USD for Jan 1 2024 - Jun 30 2024 and runs a simple backtest.
import yfinance as yf
import pandas as pd
import numpy as np
import os, json
from datetime import datetime
from importlib import util

# load strategy dynamically
spec = util.spec_from_file_location('your_strategy', os.path.join('..','your-strategy-template','your_strategy.py'))
mod = util.module_from_spec(spec)
spec.loader.exec_module(mod)

def download_hourly(symbol, start='2024-01-01', end='2024-06-30'):
    df = yf.download(symbol, start=start, end=(pd.to_datetime(end)+pd.Timedelta(days=1)).strftime('%Y-%m-%d'),
                     interval='1h', progress=False)
    if df.empty:
        raise RuntimeError(f'No data for {symbol}')
    df = df[['Open','High','Low','Close','Volume']].rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'})
    df = df.reset_index().rename(columns={'Datetime':'timestamp'})
    return df

def run_backtest():
    symbols = ['BTC-USD','ETH-USD']
    data = {s: download_hourly(s) for s in symbols}
    print('Rows per symbol:', {s: len(data[s]) for s in symbols})

    cash = 10000.0
    positions = {s: 0 for s in symbols}
    last_price = {s: None for s in symbols}
    fee = 0.001  # 0.1%
    equity_curve = []

    strategy = mod.create_strategy({'symbols': symbols, 'lookback':20, 'z_entry':1.5, 'z_exit':0.5, 'max_exposure':0.55})

    # use intersection of timestamps for alignment
    timestamps = sorted(set(ts for s in symbols for ts in data[s]['timestamp'].tolist()))
    for t in timestamps:
        for s in symbols:
            df = data[s]
            row = df[df['timestamp'] == t]
            if row.empty:
                continue
            row = row.iloc[0]
            bar = {'open': row['open'], 'high': row['high'], 'low': row['low'], 'close': row['close'], 'volume': row['volume'], 'timestamp': row['timestamp']}
            sig = strategy.generate_signal(s, bar)
            last_price[s] = row['close']
            if sig is not None:
                if sig.action == 'buy':
                    equity = cash + sum(positions[k]* (last_price.get(k) or 0) for k in symbols)
                    max_value = equity * strategy.max_exposure
                    size = int(max_value // row['close'])
                    if size > 0:
                        cost = size * row['close'] * (1 + fee)
                        if cost <= cash:
                            cash -= cost
                            positions[s] += size
                elif sig.action == 'sell':
                    sell_size = min(sig.size, positions.get(s,0))
                    if sell_size > 0:
                        proceeds = sell_size * row['close'] * (1 - fee)
                        cash += proceeds
                        positions[s] -= sell_size
                elif sig.action == 'close':
                    sell_size = positions.get(s,0)
                    if sell_size > 0:
                        proceeds = sell_size * row['close'] * (1 - fee)
                        cash += proceeds
                        positions[s] = 0
        equity = cash + sum(positions[k]* (last_price.get(k) or 0) for k in symbols)
        equity_curve.append({'timestamp': t, 'equity': equity})

    out = {'equity_curve': equity_curve, 'final_equity': equity, 'positions': positions, 'cash': cash}
    os.makedirs('reports', exist_ok=True)
    with open('reports/backtest_results.json','w') as f:
        json.dump(out, f, default=str, indent=2)
    print('Backtest complete. Final equity:', equity)

if __name__ == '__main__':
    run_backtest()
