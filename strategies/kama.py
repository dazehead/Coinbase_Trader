import talib as ta
import numpy as np
import pandas as pd
from strategies.efratio import EFratio_Strategy


class KAMA_Strategy(EFratio_Strategy):
    def __init__(self, df, efratio_window=15, **kwargs):
        super().__init__(df=df, **kwargs)

        self.efratios = self.calculate_efratios(efratio_window)

    def custom_indicator(self,close, fast_window=30, slow_window=3):

        kama = self.calculate_kama(self.efratios, close, fast_window, slow_window)
        self.ti_data = pd.Series(kama, index=self.close.index)
        

    def calculate_kama(self, efratios, close, fast_window, slow_window):
        fast_period = 30
        slow_period = 3

        fast_ma = ta.EMA(close, timeperiod=fast_window)
        slow_ma = ta.EMA(close, timeperiod=slow_window)

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