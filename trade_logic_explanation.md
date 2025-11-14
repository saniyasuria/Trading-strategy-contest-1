# Trade Logic Explanation (Final - Contest-Compliant)

Author / GitHub: https://github.com/saniyasuria

Overview:
- Short-term mean reversion on hourly log returns (interval=1h).
- Uses generate_signal(symbol, data).
- Signals: Signal(action='buy'/'sell'/'close').
- Max exposure per trade capped at 55% (0.55).
- Data period for local verification: 2024-01-01 to 2024-06-30 via Yahoo hourly candles.

Logic:
1. Rolling window of last `lookback` closes (default 20).
2. Compute log returns and z-score.
3. If z > z_entry -> sell; if z < -z_entry -> buy; if |z| < z_exit -> close.

Risk & Sizing:
- Conservative integer sizing.
- Max exposure cap ensures <=55% of equity used per trade.
- Tune lookback/thresholds to ensure >=10 trades across the period.
