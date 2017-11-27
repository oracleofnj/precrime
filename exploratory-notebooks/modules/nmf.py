"""Functions to make crime predictions."""
import numpy as np
import pandas as pd
import datetime
import csv
from .weather import load_weather_data
from .nypd_data import load_pivoted_felonies
from .nyc_shapefiles import load_census_info
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
from numpy import linalg as LA
import scipy.linalg as scla
import itertools
from scipy.interpolate import RectBivariateSpline



class nmf_model(object):
    '''
        Non-negative matrix Factorization Model : X~W*H
        '''
    def __init__(self, X_train,y_train, X_test):
        self.train_features=X_train[['COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD']].copy()
        
        self.train_features['COMPLAINT_DAY_HOUR'] = X_train['COMPLAINT_YEAR'].astype(str) + '-' + \
            X_train['COMPLAINT_MONTH'].astype(str) + '-'+ \
            X_train['COMPLAINT_DAY'].astype(str) + '-'+ \
            X_train['COMPLAINT_HOURGROUP'].astype(str)
        for crime in y_train.columns: self.train_features[crime]=y_train[crime]
        
        self.test_features=X_test[['COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'COMPLAINT_HOURGROUP', 'ADDR_PCT_CD']].copy()
        self.test_features['COMPLAINT_DAY_HOUR'] = X_test['COMPLAINT_YEAR'].astype(str) + '-' + \
            X_test['COMPLAINT_MONTH'].astype(str) + '-'+\
            X_test['COMPLAINT_DAY'].astype(str) + '-'+\
            X_test['COMPLAINT_HOURGROUP'].astype(str)
        for crime in y_train.columns: self.test_features[crime]=""
        
        self.X_train=X_train
        self.y_train=y_train
        self.X_test=X_test
        
        pct_set=sorted(list(set(X_train['ADDR_PCT_CD'])))
        pct_set=zip(pct_set,range(len(pct_set)))
        self.code2idx={x[0]:x[1] for x in pct_set  }
        self.idx2code={X[1]:x[0] for x in pct_set }
        
        
        train_datetime=X_train[['COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'COMPLAINT_HOURGROUP']]
        test_datetime=X_test[['COMPLAINT_YEAR', 'COMPLAINT_MONTH', 'COMPLAINT_DAY', 'COMPLAINT_HOURGROUP']]
        self.train_datetime = sorted(list(set([tuple(x) for x in train_datetime.values])))
        self.test_datetime = sorted(list(set([tuple(x) for x in test_datetime.values])))
        self.all_datetime=[]
        self.all_datetime.extend(self.train_datetime)
        self.all_datetime.extend(self.test_datetime)
                self.all_datetime=sorted(self.all_datetime)

def update(self, X,W,H):
    n1, n2 = X.shape
        p= np.divide(X, (np.dot(W, H)+(10**-16)*np.ones((n1, n2))))
        normal=W/(W.sum(axis=0)+10**-16)
        tmp= np.dot(np.transpose(normal),p)
        H= np.multiply(H,tmp)
        p= np.divide(X, (np.dot(W, H)+(10**-16)*np.ones((n1, n2))))
        normal=np.transpose(np.transpose(H)/(np.transpose(H).sum(axis=0)+10**-16))
        tmp= np.dot(p,np.transpose(normal))
        W= np.multiply(W,tmp)
        return H, W
    
    def fit(self, crime_type):
        np.random.seed(3213)
        self.W=np.random.uniform(low=0.1,high=2,size=(len(self.code2idx.keys()),10))
        self.H=np.random.uniform(low=0.1, high=2, size=(10,540))
        for date in self.test_datetime:
            
            date_val='-'.join(list(map(str,date)))
            print('calculating for the time stamp: '+date_val)
            X_T=[]
            
            idx=self.all_datetime.index(date)
            prev_year=self.all_datetime[idx-540:idx]
            for p_date in prev_year:
                t_stamp=['']*len(self.code2idx.keys())
                p_date_val='-'.join(list(map(str,p_date)))
                temp=self.train_features.loc[self.train_features['COMPLAINT_DAY_HOUR'] == p_date_val]
                if not len(temp):
                    temp=self.test_features.loc[self.test_features['COMPLAINT_DAY_HOUR'] == p_date_val]
                for index, row in temp.iterrows():
                    t_stamp[self.code2idx[row['ADDR_PCT_CD']]]=int(row[crime_type])
                
                X_T.append(t_stamp)
            X_T=np.array(X_T)
            X=X_T.T
            print('X created for '+date_val+' X shape:'+str(X.shape))
            n1, n2 = X.shape
            
            for i in range(20):
                self.H, self.W = self.update(X,self.W,self.H)
    
    a,b=range(self.H.shape[0]),range(self.H.shape[1])
        f_interp = RectBivariateSpline(a,b, self.H)
            new_val= f_interp(a,self.H.shape[1]).reshape(self.H.shape[0],1)
            H_new=np.hstack((self.H,new_val))
            X_new=np.dot(self.W,H_new)
            
            pred_values=X_new[:,-1]
            print('done for '+date_val)
            for index, row  in self.test_features.loc[self.test_features['COMPLAINT_DAY_HOUR'] == date_val].iterrows():
                self.test_features.loc[index,crime_type]=pred_values[self.code2idx[row['ADDR_PCT_CD']]]
return self.test_features



