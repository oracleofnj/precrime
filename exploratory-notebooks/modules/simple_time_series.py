"""Functions to make crime predictions using a time-series model."""
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


def simple_time_series_model(X_train, y_train, X_test, y_test):
    """Moving average of last four weeks."""
    def get_decimal_date(X):
        y = np.array(X['COMPLAINT_YEAR']-1970, dtype='<M8[Y]')
        m = np.array(X['COMPLAINT_MONTH']-1, dtype='<m8[M]')
        d = np.array(X['COMPLAINT_DAY']-1, dtype='<m8[D]')
        mid_dates = y+m+d
        m2 = np.zeros_like(y, dtype='<m8[M]')
        d2 = np.zeros_like(y, dtype='<m8[D]')
        start_dates = y+m2+d2
        y3 = y + 1
        end_dates = y3+m2+d2
        decimal_date = pd.Series(
            X['COMPLAINT_YEAR'].values + (
                (mid_dates - start_dates) / (end_dates - start_dates)
            ),
            index=X.index
        )
        return decimal_date

    X_all = pd.concat([X_train, X_test])
    X_all['DECIMAL_DATE'] = get_decimal_date(X_all)
    y_all = pd.concat([y_train, y_test])
    all_all = pd.merge(X_all, y_all, left_index=True, right_index=True)

    y_pred = X_test[[
        'COMPLAINT_YEAR',
        'COMPLAINT_MONTH',
        'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP',
        'ADDR_PCT_CD'
    ]].copy()

    buckets = X_test[[
        'COMPLAINT_YEAR',
        'COMPLAINT_MONTH',
        'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP',
        'COMPLAINT_DAYOFWEEK',
    ]].copy().drop_duplicates()
    buckets['DECIMAL_DATE'] = get_decimal_date(buckets)
    preds = []
    y_train_dvs = y_train.select_dtypes(exclude=['object']).columns
    for index, bucket in buckets.iterrows():
        comparison = all_all[
            (all_all['COMPLAINT_DAYOFWEEK'] == bucket['COMPLAINT_DAYOFWEEK']) &
            (all_all['COMPLAINT_HOURGROUP'] == bucket['COMPLAINT_HOURGROUP']) &
            (all_all['DECIMAL_DATE'] < (bucket['DECIMAL_DATE'] - 6/365)) &
            (all_all['DECIMAL_DATE'] > (bucket['DECIMAL_DATE'] - 37/365))
        ]
        pred = comparison.groupby('ADDR_PCT_CD')[y_train_dvs].mean()
        pred.reset_index(inplace=True)
        for fld in [
            'COMPLAINT_YEAR',
            'COMPLAINT_MONTH',
            'COMPLAINT_DAY',
            'COMPLAINT_HOURGROUP',
        ]:
            pred[fld] = bucket[fld]
        preds.append(pred)
    all_preds = pd.concat(preds)
    return y_pred.reset_index().merge(
        all_preds,
        how='left'
    ).set_index('index').fillna(0)
