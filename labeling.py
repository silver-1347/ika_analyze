# coding: utf-8

import os
import glob
import cv2

import numpy as np
from sklearn.svm import SVC
from sklearn.grid_search import GridSearchCV
from sklearn.decomposition import PCA

def flatten(data):
    return data.reshape(1,1,-1)[0][0]

# 諸設定

results_dir = 'Results'
others_dir = 'Others'
unlabeled_dir = 'Images'

rec = (500,500)

# データロード

results_files = glob.glob(results_dir + '/*.jpg')
others_files = glob.glob(others_dir + '/*.jpg')
unlabeled_files = glob.glob(unlabeled_dir + '/*.jpg')

results = [cv2.resize(cv2.imread(filename,0),rec) for filename in results_files]
others = [cv2.resize(cv2.imread(filename,0),rec) for filename in others_files]
labels = np.array(([1] * len(results_files)) + ([0] * len(others_files)))

unlabeleds = [cv2.resize(cv2.imread(filename,0),rec) for filename in unlabeled_files]

# flatten

results_flatten = np.array(list(map(flatten,results)))
others_flatten = np.array(list(map(flatten,others)))
all_flatten = np.r_[results_flatten,others_flatten]

unlabeled_flatten = np.array(list(map(flatten,unlabeleds)))

# 主成分分析してSVM学習、識別
pca = PCA(n_components=3)
pca.fit(all_flatten)

tuned_parameters = [
    {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
    {'C': [1, 10, 100, 1000], 'kernel': ['rbf'], 'gamma': [0.001, 0.0001]},
    {'C': [1, 10, 100, 1000], 'kernel': ['poly'], 'degree': [2, 3, 4], 'gamma': [0.001, 0.0001]},
    {'C': [1, 10, 100, 1000], 'kernel': ['sigmoid'], 'gamma': [0.001, 0.0001]}]

score = 'f1'
clf = GridSearchCV(
    SVC(), # 識別器
    tuned_parameters, # 最適化したいパラメータセット 
    cv=5, # 交差検定の回数
    scoring='%s_weighted' % score ) # モデルの評価関数の指定

clf.fit(X=pca.transform(all_flatten), y=labels)
predictions = clf.predict(pca.transform(unlabeled_flatten))

predicted_results = np.array(unlabeled_files)[predictions==1]
predicted_others = np.array(unlabeled_files)[predictions==0]

for f in predicted_results:
    name = os.path.basename(f)
    os.rename(f,os.path.join(results_dir,name))

for f in predicted_others:
    name = os.path.basename(f)
    os.rename(f,os.path.join(others_dir,name))
