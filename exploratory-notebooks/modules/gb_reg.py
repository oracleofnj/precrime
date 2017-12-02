"""Functions to make crime predictions.
Use Gradient Boosting Regression
"""
import numpy as np
import pandas as pd
import datetime
import csv
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import cross_val_score
from skopt import gp_minimize
class GBR(object):
    
    def __init__(self, X_train, y_train,  cv=5):
       
        self.X_train=X_train
        self.y_train=y_train
        self.cv=cv
    def objective(self,params):

        max_depth, learning_rate, max_features, min_samples_split, min_samples_leaf = params
        reg = GradientBoostingRegressor(n_estimators=30, random_state=0)
        reg.set_params(max_depth=max_depth,
                   learning_rate=learning_rate,
                   max_features=max_features,
                   min_samples_split=min_samples_split, 
                   min_samples_leaf=min_samples_leaf)

        return -np.mean(cross_val_score(reg, self.X_train, self.y_train, cv=5,
                                    scoring="neg_mean_absolute_error"))

    def predict(self, params , X_test):
        max_depth, learning_rate, max_features, min_samples_split, min_samples_leaf = params
        reg = GradientBoostingRegressor(n_estimators=30, random_state=0,max_depth=max_depth,
                   learning_rate=learning_rate,
                   max_features=max_features,
                   min_samples_split=min_samples_split, 
                   min_samples_leaf=min_samples_leaf )
        fit = reg.fit(self.X_train,self.y_train)
        return reg.predict(X_test)


def gbr_model_bo(X_train, y_train, X_test):
    """Example model to perform gradient Boosted Regression on each felony type alongwith hyperparameter tuning."""
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
    np.random.seed(324)
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


    n_features = X_train_features.shape[1]

    space  = [(1, 5),                           # max_depth
          (10**-5, 10**0, "log-uniform"),   # learning_rate
          (1, n_features),                  # max_features
          (2, 100),                         # min_samples_split
          (1, 100)]                         # min_samples_leaf
    store={}
    for crime_type in crime_types:
        model=GBR(X_train_features, y_train[crime_type])
        print('...model initialised for '+ crime_type)
        res_gp = gp_minimize(model.objective, space, n_calls=100, random_state=0)
        print('...obtained hyperparameters')
        print('[max_depth, learning_rate, max_features, min_samples_split, min_samples_leaf] =' +str(res_gp.x))
        store[crime_type] = res_gp.x
        print('prediction made for '+ crime_type)
    return store


def gbr_model(X_train, y_train, X_test, params):
    """Example model to perform gradient Boosted Regression on each felony type alongwith hyperparameter tuning."""
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
    np.random.seed(324)
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


    n_features = X_train_features.shape[1]

    space  = [(1, 5),                           # max_depth
          (10**-5, 10**0, "log-uniform"),   # learning_rate
          (1, n_features),                  # max_features
          (2, 100),                         # min_samples_split
          (1, 100)]                         # min_samples_leaf

    for crime_type in crime_types:
        model=GBR(X_train_features, y_train[crime_type])
        print('...model initialised for '+ crime_type)
        y_pred[crime_type] = model.predict(params[crime_type],X_test_features)
        print('prediction made for '+ crime_type)
    return y_pred

