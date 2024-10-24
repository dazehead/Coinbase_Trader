import pandas as pd
import utils
import sqlite3 as sql

def volume_conversion():
    times_to_resample = ['ONE_MINUTE', 'FIVE_MINUTE', 'THIRTY_MINUTE', 'ONE_HOUR', 'TWO_HOUR', 'SIX_HOUR', 'ONE_DAY']
    for granularity in times_to_resample:
        conn = sql.connect(f'database/{granularity}.db')
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = pd.read_sql_query(query, conn)
        
        for table in tables['name']:
            clean_table_name = '-'.join(table.split('_')[:2])
            data = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
            data['date'] = pd.to_datetime(data['date'], errors='coerce')
            data.set_index('date', inplace=True)
            move_decimal = lambda val: int(''.join(f"{val:.10f}".rstrip('0').split('.'))) if isinstance(val, float) else val
            data['volume'] = data['volume'].apply(move_decimal)
            utils.export_historical_to_db({clean_table_name: data}, granularity)



def get_historical_from_db(granularity, symbols: list = [], num_days: int = None):
    conn = sql.connect(f'database/{granularity}.db')
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables = pd.read_sql_query(query, conn)
    tables_data = {}
    
    for table in tables['name']:
        clean_table_name = '-'.join(table.split('_')[:2])

        # If symbols are provided, skip tables that are not in the symbol list
        if symbols and clean_table_name not in symbols:
            continue

        # Retrieve data from the table
        data = pd.read_sql_query(f'SELECT * FROM "{table}"', conn)
        data['date'] = pd.to_datetime(data['date'], errors='coerce')
        data.set_index('date', inplace=True)

        # If num_days is provided, filter the data based on the most recent date
        if num_days is not None:
            last_date = data.index.max()  # Find the most recent date in the dataset
            start_date = last_date - pd.Timedelta(days=num_days)
            data = data.loc[data.index >= start_date]

        # Store the data in the dictionary
        tables_data[clean_table_name] = data
    
    conn.close()
    return tables_data

def resample_dataframe_from_db(granularity='ONE_MINUTE'):
    """
    Resamples data from the database for different timeframes based on the granularity.
    """
    times_to_resample = {
        'FIVE_MINUTE': '5min',
        'FIFTEEN_MINUTE': '15min',
        'THIRTY_MINUTE': '30min',
        'ONE_HOUR': '1h',
        'TWO_HOUR': '2h',
        'SIX_HOUR': '6h',
        'ONE_DAY': '1D'
    }


    dict_df = get_historical_from_db(granularity=granularity)

    resampled_dict_df = {}

    for key, value in times_to_resample.items():
        for symbol, df in dict_df.items():
            df = df.sort_index()

            df_resampled = df.resample(value).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })

            df_resampled.dropna(inplace=True)

            print(f"Resampled {symbol} to {key}")
            resampled_dict_df[symbol] = df_resampled

        utils.export_historical_to_db(resampled_dict_df, granularity=key)

    print("Resampling completed.")

