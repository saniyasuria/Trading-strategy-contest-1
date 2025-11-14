from base_bot_template.strategy_interface import BaseStrategy, Signal
import numpy as np

class YourStrategy(BaseStrategy):
    """Contest-compliant mean-reversion strategy.
    - Implements generate_signal(symbol, data)
    - Uses Signal(action='buy'/'sell'/'close')
    - Enforces max exposure cap (0.55 of portfolio)
    """

    def __init__(self, config):
        super().__init__(config)
        self.lookback = int(config.get('lookback', 20))
        self.z_entry = float(config.get('z_entry', 1.5))
        self.z_exit = float(config.get('z_exit', 0.5))
        self._symbols = getattr(self, 'symbols', config.get('symbols', ['BTC-USD','ETH-USD']))
        self._prices = {s: [] for s in self._symbols}
        self.max_exposure = float(config.get('max_exposure', 0.55))
        self._min_trade_gap = int(config.get('min_trade_gap', 1))  # optional spacing

    def generate_signal(self, symbol, data):
        """Called each bar. Return Signal(action='buy'/'sell'/'close') or None."""
        close = data.get('close')
        if close is None:
            return None

        if symbol not in self._prices:
            self._prices[symbol] = []
        self._prices[symbol].append(float(close))
        if len(self._prices[symbol]) > self.lookback + 5:
            self._prices[symbol].pop(0)

        if len(self._prices[symbol]) < self.lookback:
            return None

        prices = np.array(self._prices[symbol][-self.lookback:])
        rets = np.diff(np.log(prices + 1e-12))
        if rets.size < 2:
            return None

        z = (rets[-1] - rets.mean()) / (rets.std() + 1e-12)

        if z > self.z_entry:
            size = self._compute_size(symbol)
            if size <= 0:
                return None
            return Signal(symbol=symbol, action='sell', size=size)
        elif z < -self.z_entry:
            size = self._compute_size(symbol)
            if size <= 0:
                return None
            return Signal(symbol=symbol, action='buy', size=size)
        elif abs(z) < self.z_exit:
            return Signal(symbol=symbol, action='close', size=0)

        return None

    def _compute_size(self, symbol):
        """Compute integer size such that position value <= max_exposure * equity."""
        try:
            equity = float(self.get_portfolio_value())
        except Exception:
            equity = 10000.0
        max_value = equity * self.max_exposure
        price = self.get_last_price(symbol) or 1.0
        size = int(max_value // price)
        return max(1, size)

def create_strategy(config):
    return YourStrategy(config)
