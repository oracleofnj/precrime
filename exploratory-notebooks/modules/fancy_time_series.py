"""Functions to make crime predictions using a time-series model."""
import numpy as np
import pandas as pd


def fancy_time_series_model(X_train, y_train, X_test, y_test):
    """Calculate results using a more complicated time series model.

    Over the previous year, calculates what fraction of the total crimes
    over the course of a week are typically represented by this bucket.

    Calculates the total number of crimes over the prior four weeks, then
    multiplies by the fraction to estimate the crimes for a particular bucket.
    """
    def get_np_dates(X):
        y = np.array(X['COMPLAINT_YEAR']-1970, dtype='<M8[Y]')
        m = np.array(X['COMPLAINT_MONTH']-1, dtype='<m8[M]')
        d = np.array(X['COMPLAINT_DAY']-1, dtype='<m8[D]')
        mid_dates = y+m+d
        return pd.Series(mid_dates, index=X.index)

    def get_one_decimal_date(y, m, d):
        y_np = np.array([y - 1970], dtype='<M8[Y]')
        m_np = np.array([m - 1], dtype='<m8[M]')
        d_np = np.array([d - 1], dtype='<m8[D]')
        return (y_np + m_np + d_np)[0]

    def get_52_weeks_ago(y, m, d):
        today_np = get_one_decimal_date(y, m, d)
        lastyear_np = today_np - np.timedelta64(7 * 52, 'D')
        return lastyear_np

    def get_4_weeks_ago(y, m, d):
        today_np = get_one_decimal_date(y, m, d)
        lastmonth_np = today_np - np.timedelta64(7 * 4, 'D')
        return lastmonth_np

    X_all = pd.concat([X_train, X_test])
    X_all['DECIMAL_DATE'] = get_np_dates(X_all)
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
        'COMPLAINT_DAYOFWEEK',
    ]].copy().drop_duplicates()
    buckets['DECIMAL_DATE'] = get_np_dates(buckets)
    preds = []
    y_train_dvs = y_train.select_dtypes(exclude=['object']).columns
    for index, bucket in buckets.iterrows():
        comparison_fullyear = all_all[
            (all_all['DECIMAL_DATE'] >= get_52_weeks_ago(
                bucket['COMPLAINT_YEAR'],
                bucket['COMPLAINT_MONTH'],
                bucket['COMPLAINT_DAY'])) &
            (all_all['DECIMAL_DATE'] < get_one_decimal_date(
                bucket['COMPLAINT_YEAR'],
                bucket['COMPLAINT_MONTH'],
                bucket['COMPLAINT_DAY']))
        ]
        total_felonies_last_year = np.sum(
            comparison_fullyear[y_train_dvs].values
        )
        comparison_lastmonth = all_all[
            (all_all['DECIMAL_DATE'] >= get_4_weeks_ago(
                bucket['COMPLAINT_YEAR'],
                bucket['COMPLAINT_MONTH'],
                bucket['COMPLAINT_DAY'])) &
            (all_all['DECIMAL_DATE'] < get_one_decimal_date(
                bucket['COMPLAINT_YEAR'],
                bucket['COMPLAINT_MONTH'],
                bucket['COMPLAINT_DAY']))
        ]
        total_felonies_last_month = np.sum(
            comparison_lastmonth[y_train_dvs].values
        )

        comparison_fullyear_bucketed = comparison_fullyear.groupby([
            'COMPLAINT_DAYOFWEEK', 'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD'
        ])[y_train_dvs].sum()
        fullweek_pred = (
            comparison_fullyear_bucketed *
            (total_felonies_last_month / 4) /
            total_felonies_last_year
        ).reset_index()
        pred = fullweek_pred[
            fullweek_pred['COMPLAINT_DAYOFWEEK'] ==
            bucket['COMPLAINT_DAYOFWEEK']
        ].copy()
        for fld in [
            'COMPLAINT_YEAR',
            'COMPLAINT_MONTH',
            'COMPLAINT_DAY',
        ]:
            pred[fld] = bucket[fld]
        preds.append(pred)
    all_preds = pd.concat(preds)
    return y_pred.reset_index().merge(
        all_preds,
        how='left'
    ).set_index('index').fillna(0)
