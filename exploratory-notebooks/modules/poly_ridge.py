"""Functions to make crime predictions."""
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge


def poly_ridge_model(X_train, y_train, X_test):
    """Ridge regression with categorical features."""
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

    def add_categorical_features_and_dates(X):
        X_features = X[[
            'ADDR_PCT_CD',
            'COMPLAINT_MONTH',
            'temperature',
            'precipIntensity'
        ]].copy()
        X_features['COMPLAINT_DAY_HOUR'] = \
            X['COMPLAINT_DAYOFWEEK'].astype(str) + '_' + \
            X['COMPLAINT_HOURGROUP'].astype(str)
        decimal_date, year_frac = get_decimal_date(X)
        X_features['DECIMAL_DATE'] = decimal_date
        X_features['YEAR_FRAC'] = year_frac
        X_features['temp_sq'] = X_features['temperature'] ** 2
        X_features['precip_sq'] = X_features['precipIntensity'] ** 2
        X_features['date_sq'] = X_features['DECIMAL_DATE'] ** 2
        X_features['yf_sq'] = X_features['YEAR_FRAC'] ** 2
        X_features['date_cube'] = X_features['DECIMAL_DATE'] ** 3
        X_features['yf_cube'] = X_features['YEAR_FRAC'] ** 3
        return pd.get_dummies(
            X_features,
            columns=['ADDR_PCT_CD', 'COMPLAINT_MONTH', 'COMPLAINT_DAY_HOUR']
        )

    X_train_features = add_categorical_features_and_dates(X_train)
    X_test_features = add_categorical_features_and_dates(X_test)
    y_pred = X_test[[
        'COMPLAINT_YEAR',
        'COMPLAINT_MONTH',
        'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP',
        'ADDR_PCT_CD'
    ]].copy()

    y_train_dvs = y_train.select_dtypes(exclude=['object'])
    ridge = Ridge()
    ridge.fit(X_train_features, y_train_dvs)
    y_pred_dvs = ridge.predict(X_test_features)

    for i, crime_type in enumerate(y_train_dvs.columns):
        y_pred[crime_type] = y_pred_dvs[:, i]

    return y_pred
