"""Functions to make crime predictions.
Use MultinomialNB and Random Forest to predict
"""
import numpy as np
import pandas as pd
import datetime
import csv
from sklearn.ensemble import RandomForestRegressor

# Use RandomForestRegressor
def sample_model_RF(X_train, y_train, X_test):
    """Example model to perform ridge regression on each felony type."""
    def add_categorical_features(X):
        X_features = X[[
            'ADDR_PCT_CD',
            'COMPLAINT_MONTH',
            'temperature',
            'precipIntensity'
        ]].copy()
        X_features['COMPLAINT_DAY_HOUR'] = \
            X['COMPLAINT_DAYOFWEEK'].astype(str) + '_' + \
            X['COMPLAINT_HOURGROUP'].astype(str)
        return pd.get_dummies(
            X_features,
            columns=['ADDR_PCT_CD', 'COMPLAINT_MONTH', 'COMPLAINT_DAY_HOUR']
        )

    X_train_features = add_categorical_features(X_train)
    X_test_features = add_categorical_features(X_test)
    y_pred = X_test[[
        'COMPLAINT_YEAR',
        'COMPLAINT_MONTH',
        'COMPLAINT_DAY',
        'COMPLAINT_HOURGROUP',
        'ADDR_PCT_CD'
    ]].copy()
    crime_types = y_train.select_dtypes(exclude=['object']).columns

    for crime_type in crime_types:
        clf = RandomForestRegressor(max_depth=2, random_state=0)    
        clf.fit(X_train_features, y_train[crime_type])
        y_pred[crime_type] = clf.predict(X_test_features)

    return y_pred
