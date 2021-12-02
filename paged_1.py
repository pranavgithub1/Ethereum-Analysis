import gc
from datetime import datetime

import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import test
import tracemalloc
from guppy import hpy

global PERIOD, NUM, h, currency_log_file, investor_stats_file, chunksize
period = np.timedelta64(30,'D') / np.timedelta64(1,'ns')
# h = hpy()
chunksize = 10000
currency_log_file = "currency_log_30d_2.csv"
investor_stats_file = "investor_stats_30d_2.csv"

def main():

    orphans = pd.DataFrame()
    # lines  = 11621110
    # addresses = 2,952,653

    cur_chunk = 1
    for transactions in pd.read_csv("/home/pranav/PycharmProjects/BigQuery_test/gcs_csv_data/combined.csv",chunksize=chunksize):
        # if(cur_chunk<160):
        #     cur_chunk+=1
        #     print("Skipped chunk {}".format(cur_chunk))
        #     continue
        orphans = process(transactions, orphans, cur_chunk)
        cur_chunk += 1



def process(transactions,orphans,cur_chunk):
    # Handle orphans
    # print(orphans.shape)
    # print(transactions.shape)
    print("Processing chunk {} of {} - {}".format(cur_chunk, int(11621110 / chunksize),
                                                  datetime.now().strftime("%H:%M:%S")), end="|")
    transactions = pd.concat((orphans, transactions))
    last_val = transactions["address"].iloc[-1]
    is_orphan = (transactions["address"] == last_val)
    transactions, orphans = transactions[~is_orphan], transactions[is_orphan]
    if(transactions.empty):
        print("transactions empty")
        return orphans
    # print(transactions.dtypes)
    # print(orphans.dtypes)
    # if(transactions.empty):
    #     cur_chunk+=1
    #     print("transactions empty")
    #     print(h.heap())
    #     continue
    # process chunk
    transactions['block_timestamp'] = pd.to_datetime(transactions['block_timestamp'])
    transactions = pd.DataFrame(
        transactions.values.repeat(transactions['value'].astype(int), axis=0),
        columns=transactions.columns
    ).astype(transactions.dtypes)
    transactions['block_timestamp'] = (transactions['block_timestamp'].astype(np.int64))
    # print("Finished unrolling for chunk {} - {}".format(cur_chunk,datetime.now().strftime("%H:%M:%S")))
    print("#", end="")
    currency_log = transactions.groupby(transactions.address, sort=False).apply(lambda df: pd.DataFrame(
        test.match((df['block_timestamp'].to_numpy()), (df['type'].to_numpy()))
    ))
    currency_log.columns = ['acquisition_time', 'relinquishment_time', 'holding_period']
    currency_log = currency_log[currency_log['acquisition_time'] != -1]
    currency_log.replace({'relinquishment_time': {-1: pd.NaT}, 'holding_period': {-1: period}},
                         inplace=True)
    # print("Finished LIFO for chunk {} - {}".format(cur_chunk,datetime.now().strftime("%H:%M:%S")))
    # print(currency_log.dtypes)
    print("#", end="")
    currency_log['acquisition_time'] = pd.to_datetime(currency_log['acquisition_time'], unit='ns')
    currency_log['relinquishment_time'] = pd.to_datetime(currency_log['relinquishment_time'], unit='ns')
    currency_log['holding_period'] = currency_log['holding_period'] / ((10**9)*3600)
    currency_log.reset_index(inplace=True)
    currency_log.drop('level_1', axis='columns', inplace=True)
    currency_log.columns = ['address', 'acquisition_time', 'relinquishment_time', 'holding_period']
    # print(currency_log.index)
    investor_stats = pd.DataFrame(currency_log.groupby("address", sort=False)['holding_period'].describe())
    investor_stats.columns = ['count', 'mean', 'std', 'min', 'percentile_25', 'percentile_50', 'percentile_75', 'max']

    if (cur_chunk == 1):
        currency_log.to_csv(currency_log_file)
        investor_stats.to_csv(investor_stats_file)
    else:
        investor_stats.to_csv(investor_stats_file, mode="a", header=False)
        currency_log.to_csv(currency_log_file, mode="a", header=False)
    # print("Finished chunk {} - {}".format(cur_chunk,datetime.now().strftime("%H:%M:%S")))
    print("#")
    # print(h.heap())
    return orphans

main()
