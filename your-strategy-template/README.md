# your-strategy-template (Contest-Compliant Final)

This template implements the required BaseStrategy API:
- generate_signal(symbol, data) is the single hook.
- Signals use Signal(action='buy'/'sell'/'close').
- Max exposure per trade capped at 55% (0.55).
- Designed for hourly data (interval='1h') between 2024-01-01 and 2024-06-30.

Notes:
- reports/backtest_runner.py is a local verification tool that uses yfinance to fetch hourly data.
- For official submission, follow contest guidance whether to include or omit yfinance/data-fetching.
