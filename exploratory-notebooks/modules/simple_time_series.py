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
        year_frac = pd.Series(
            (mid_dates - start_dates) / (end_dates - start_dates),
            index=X.index
        )
        return decimal_date, year_frac

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
    ]].copy().drop_duplicates()
    for index, bucket in buckets.iterrows():
        
        X_test_combined =
        print(bucket)

    return None

    y_train_dvs = y_train.select_dtypes(exclude=['object'])
    ridge = Ridge()
    ridge.fit(X_train_features, y_train_dvs)
    y_pred_dvs = ridge.predict(X_test_features)

    for i, crime_type in enumerate(y_train_dvs.columns):
        y_pred[crime_type] = np.maximum(0, y_pred_dvs[:, i])

    return y_pred
