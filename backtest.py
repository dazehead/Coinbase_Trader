import os
import pandas as pd
import utils
import datetime as dt
import wrapper
import numpy as np
import database_interaction
from coinbase.rest import RESTClient
from strategies.strategy import Strategy
from strategies.efratio import EFratio
from strategies.vwap import Vwap
from strategies.rsi import RSI
from strategies.atr import ATR
from strategies.macd import MACD
from strategies.kama import Kama
from strategies.combined_strategy import Combined_Strategy
from log import LinkedList
from hyper import Hyper
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)


api_key = os.getenv('API_ENV_KEY') #API_ENV_KEY | COINBASE_API_KEY
api_secret = os.getenv('API_SECRET_ENV_KEY') #API_SECRET_ENV_KEY | COINBASE_API_SECRET
sandbox_key = os.getenv('SANDBOX_KEY')
sandbox_rest_url = "https://api-public.sandbox.exchange.coinbase.com"

client = RESTClient(api_key=api_key, api_secret=api_secret)


symbols = ['BTC-USD', 'ETH-USD']
symbol = ['BTC-USD']
granularity = 'ONE_MINUTE'

def test_multiple_strategy():
    logbook = LinkedList()
    df_dict = database_interaction.get_historical_from_db(granularity=granularity, symbols=symbols)


    for symbol, df in df_dict.items():
        current_dict_df = {symbol:df}

        combined_strat = Combined_Strategy(current_dict_df, RSI, Kama)
        combined_strat.generate_combined_signals()
        combined_strat.graph()
        combined_strat.generate_backtest()

        logbook.insert_beginning(combined_strat)
    
    logbook.export_multiple_to_db(granularity=granularity)

#test_multiple_strategy()


def run_basic_backtest():

    dict_df = database_interaction.get_historical_from_db(granularity=granularity,
                                                          symbols=symbol,
                                                          num_days=5)
    dict_df = utils.heikin_ashi_transform(dict_df)
    #print(dict_df)
                                                   


    strat = RSI(dict_df=dict_df)
    
    strat.custom_indicator()
    strat.graph()
    strat.generate_backtest()
    pf = strat.portfolio


    # utils.export_backtest_to_db(object=strat,
    #                             granularity=granularity)


    fig = pf.plot(subplots = [
    'orders',
    'trade_pnl',
    'cum_returns',
    'drawdowns',
    'underwater',
    'gross_exposure'])
    fig.show()

    print(pf.stats())
#run_basic_backtest()




def run_hyper():
    timestamps = wrapper.get_unix_times(granularity=granularity, days=3)

    dict_df = wrapper.get_candles(client=client,
                     symbols=symbol,
                     timestamps=timestamps,
                     granularity=granularity)
    
    strat = MACD(dict_df)

    hyper = Hyper(strategy_object=strat,
                  close=strat.close,
                  fast_period=np.arange(5, 50, step=5),
                  slow_period=np.arange(50, 100, step=5),
                  signal_period=np.arange(3, 50, step=5))
    print(hyper.returns.to_string())
    print(type(hyper.returns))
    utils.export_hyper_to_db(hyper.returns, strat, granularity)

    print(f"The maximum return was {hyper.returns.max()}\nfast_period: {hyper.returns.idxmax()[0]}\nslow_period: {hyper.returns.idxmax()[1]}\nsignal_perido: {hyper.returns.idxmax()[2]}")
#run_hyper()

def testing():
    timestamps = wrapper.get_unix_times(granularity=granularity, days=3)

    dict_df = wrapper.get_basic_candles(client=client,
                     symbols=symbol,
                     timestamps=timestamps,
                     granularity=granularity)
    
    for key, value in dict_df.items():
        print(key)
        print(value)
testing()