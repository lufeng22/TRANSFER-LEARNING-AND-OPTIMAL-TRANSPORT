#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 14:13:47 2019

@author: kenneth
"""


from __future__ import absolute_import
import os
import warnings
import numpy as np
import time
from scipy.io import loadmat
from sklearn.preprocessing import MinMaxScaler
from KPCA import kPCA
from sklearn.neighbors import KNeighborsClassifier
from PCA import PCA
from utils import EvalC
from sklearn.exceptions import DataConversionWarning

#path = '/home/kenneth/Documents/MLDM M2/ADVANCE_ML/TRANSFER LEARNING/DATASET'
#data = loadmat(os.path.join(path, 'amazon.mat'))
#X_w = data['fts']
#y_w = data['labels']
#
#data_d = loadmat(os.path.join(path, 'webcam.mat'))
#X_d = data_d['fts']
#y_d = data_d['labels']

#%%

class subspacealignment(EvalC):
    def __init__(self):
        '''
        Domain Adaptation via Subspace alignment
        :References: https://hal.archives-ouvertes.fr/hal-00869417/document
                    https://arxiv.org/abs/1409.5241
        '''
        super().__init__()
        return
    
    def fit_predict(self, ds_x = None, ds_y = None, dt_x = None, \
            dt_y = None, d = None, type = None, m_kernel = None):
        '''Domain Adaptation using Subspace Alignment
        :param: ds_x: NxD
        :param: ds_y: Dx1
        :param: dt_x: NxD
        :param: dt_y: Dx1
        :param: d: Number of principal components
        '''
        if ds_x is None:
            raise IOError('Source Input data in required')
        else:
            self.ds_x = ds_x
        if ds_y is None:
            raise IOError('Source Input labels in required')
        else:
            self.ds_y = ds_y.ravel()
            
        if dt_x is None:
            raise IOError('Target Input data in required')
        else:
            self.dt_x = dt_x
        if dt_y is None:
            raise IOError('Target Input labels in required')
        else:
            self.dt_y = dt_y.ravel()
        if d is None:
            d = 2
            self.d = d
        else:
            self.d = d
        if not m_kernel:
            m_kernel = 'linear'
            self.m_kernel = m_kernel
        else:
            self.m_kernel = m_kernel
        #ignore warning when scaling data using MinMaxScaler
        warnings.filterwarnings('ignore', category = DataConversionWarning)
        #find PCA for Source domain after scaling
        X_w = MinMaxScaler().fit_transform(self.ds_x).astype(float) #scale source data
        if not type:
            X_s = kPCA(k = self.d, kernel = self.m_kernel).fit(X_w.T) #perform PCA
        else:
            X_s = PCA(k = self.d).fit(X_w)
        X_s = X_s.components_.T #get components
        
        #PCA for target domain after scaling
        X_d = MinMaxScaler().fit_transform(self.dt_x).astype(float) #scale target data
        if not type:
            X_t = kPCA(k = self.d, kernel = self.m_kernel).fit(X_d.T) #perform PCA
        else:
            X_t = PCA(k = self.d).fit(X_d)
        self.X_t = X_t.components_.T #get components
        #compute source and target projections using subspace alignment matrix
        self.X_a = X_s.dot(X_s.T.dot(self.X_t))
        self.S_a = self.ds_x.dot(self.X_a) #source projection
        self.T_a = self.dt_x.dot(self.X_t) #target projection
        print(f'>>>> Done with Subspace alingment and Data projection >>>>')
        #perform classification
        '''
        Fit a 1-NN classifier on S_a and make predictions on T_a
        '''
        print('*'*40)
        print('Initializing 1-Nearest Neighbour classifier')
        self.classifier = KNeighborsClassifier(n_neighbors = 1)
        self.classifier.fit(self.S_a, self.ds_y)
        print('>>>> Done fitting source domain >>>>')
        self.ypred = self.classifier.predict(self.T_a)
        self.accuracy = EvalC.accuary_multiclass(self.dt_y, self.ypred)
        print(f'Accuracy: {self.accuracy}')
        return self
        
class optimaltransport(EvalC):
    def __init__(self):
        '''Optimal Transport
        '''
        super().__init__()
        return
    
    def fit_predict(self, ds_x = None, ds_y = None, dt_x = None, dt_y = None):
        '''
        '''
        import ot
        from scipy.spatial.distance import cdist
        if ds_x is None:
            raise IOError('Source Input data in required')
        else:
            self.ds_x = ds_x
        if ds_y is None:
            raise IOError('Source Input data in required')
        else:
            self.ds_y = ds_y.ravel()
        if dt_x is None:
            raise IOError('Source Input data in required')
        else:
            self.dt_x = dt_x
        if dt_y is None:
            raise IOError('Source Input data in required')
        else:
            self.dt_y = dt_y.ravel()
        N_s, D_s = self.ds_x.shape
        N_t, D_t = self.dt_x.shape
        a = np.ones(N_s)
        b = np.ones(N_t)
        self.M = cdist(self.ds_x, self.dt_x)
        self.G = ot.sinkhorn(a, b, self.M, 5, method = 'sinkhorn')
        print(f'>>>> Finnished running Sinkhorn from POT library >>>>' )
        print('*'*40)
        self.S_a = self.G.dot(self.dt_x)
        print('>>>> Transported Source to target domain using coupling matrix')
        print('*'*40)
        print('Initializing 1-Nearest Neighbour classifier')
        self.classifier = KNeighborsClassifier(n_neighbors = 1)
        self.classifier.fit(self.S_a, self.ds_y)
        print('>>>> Done fitting source domain >>>>')
        self.ypred = self.classifier.predict(self.dt_x)
        self.accuracy = EvalC.accuary_multiclass(self.dt_y, self.ypred)
        print(f'Accuracy: {self.accuracy}')
        return self

        
#%% Testing
        
#subalignacc = subspacealignment().fit_predict(X_w, y_w, X_d, y_d, d = 100, m_kernel = 'linear')
#
#ot = optimaltransport().fit_predict(X_w, y_w, X_d, y_d)









