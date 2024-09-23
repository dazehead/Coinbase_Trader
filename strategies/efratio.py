import numpy as np
import pandas as pd
import talib as ta
from strategies.strategy import Strategy
from utils import format_signals


class EFratio_Strategy(Strategy):
    """KAMA IS NOT CORRECT AT THE MOMENT ONLY USING EFRATIO FOR STRATEGY"""
    def __init__(self, df, **kwargs):
        super().__init__(df = df, **kwargs)

    def custom_indicator(self, close, efratio_window, ef_threshold_buy, ef_threshold_sell):
        """SELLING THRESHOLD IS ONLY THERE FOR TESTING NEED TO HYPER TEST SELLING"""
        efratios = self.calculate_efratios(efratio_window)
        #kama = self.calculate_kama(efratios, close)
        self.ti_data = pd.Series(kama, index=self.close.index)

        # for trading
        buy_signal = efratios > ef_threshold_buy
        sell_signal = efratios < ef_threshold_sell

        signals = self.generate_signals(buy_signal, sell_signal)

        return signals
 
    
    def calculate_efratios(self, efratio_window):
        efratios = []
        close = self.close
        for i in range(len(close) - efratio_window + 1):
            window_prices = close[i:i + efratio_window]
            window_efratio = self._efratio(list(window_prices))
            efratios.append(window_efratio)
        
        zeros = np.zeros(efratio_window-1)
        efratios = np.concatenate((zeros, efratios))
        efratios = pd.Series(efratios, index=close.index)
        
        return efratios
    
    def _efratio(self, prices):
        price_changes = [prices[i]-prices[i-1] for i in range(1, len(prices))]
        absolute_price_changes = [abs(change) for change in price_changes]
        net_price_change = prices[-1] - prices[0]
        sum_absolute_price_changes = sum(absolute_price_changes)
        if sum_absolute_price_changes == 0:
            return 0
        kaufman_ratio = net_price_change / sum_absolute_price_changes

        return round(kaufman_ratio, 3)
    
    def calculate_kama(self, efratios, close):
        fast_period = 30
        slow_period = 3

        fast_ma = ta.EMA(close, timeperiod=fast_period)
        slow_ma = ta.EMA(close, timeperiod=slow_period)

        kama = np.full_like(close, np.nan)

        fastest = (2/ (fast_ma + 1))
        slowest = (2/ (slow_ma + 1))

        mapping = {i: 2- 0.043 * (i-1) for i in range(1, 21)}
        keys = np.minimum(np.round(close), 20).astype(int)
        n_values = np.array([mapping[key] for key in keys])

        k=60
        x = k/ np.power(close, n_values)

        smoothing_constant = (efratios * (fastest - slowest) + slowest) ** x
        kama[fast_period -1] = close[fast_period - 1]

        for i in range(fast_period, len(close)):
            kama[i] = kama[i-1] + smoothing_constant[i] * close[i] - kama[i-1]
        
        return kama
        