import time
import uuid

import numpy as np
from matplotlib import pyplot as plt

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline

import mne

from mne.channels import make_standard_montage
from mne.datasets import eegbci
from mne.decoding import CSP
from mne.io import concatenate_raws, read_raw_edf, read_raw_eeglab

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from mne.decoding import Vectorizer


raw_train = read_raw_eeglab('MI_merged_train.set', preload = 'True')
raw_test = read_raw_eeglab('MI_merged_test.set', preload = 'True')

event_id = {"right": 1, "left": 2, "both": 3} 

tmin, tmax = -1.0, 4.0

epochs_tr = mne.Epochs(
    raw_train,
    event_id=["right","left"], 
    tmin=tmin,
    tmax=tmax,
    proj=True,
    baseline=None,
    preload=True,
)

epochs_ts = mne.Epochs(
    raw_test,
    event_id=["right","left"], 
    tmin=tmin,
    tmax=tmax,
    proj=True,
    baseline=None,
    preload=True,
)

epochs_train = epochs_tr.copy().crop(tmin=-1.0, tmax=3.0)
labels_tr = epochs_tr.events[:, -1] - 5
labels_ts = epochs_ts.events[:, -1] - 5

# Define a monte-carlo cross-validation generator (reduce variance):
scores = []
epochs_data = epochs_tr.get_data(copy=False)
epochs_data_train = epochs_train.get_data(copy=False)
epochs_data_test = epochs_ts.get_data(copy=False)

print(epochs_data_test)

cv = ShuffleSplit(5, test_size=0.10, random_state=42)
cv_split = cv.split(epochs_data_train)

# Assemble a classifier
vectorizer = Vectorizer()
scaler = StandardScaler()
logR = LogisticRegression()
lda = LinearDiscriminantAnalysis()
csp = CSP(n_components=8, reg=None, log=True, norm_trace=False)

# Use scikit-learn Pipeline with cross_val_score function
clf = Pipeline([("CSP", csp), ("logR",logR)])
scores = cross_val_score(clf, epochs_data_train, labels_tr, cv=cv, n_jobs=None)

# Printing the results
class_balance = np.mean(labels_tr == labels_tr[0])
class_balance = max(class_balance, 1.0 - class_balance)
print(scores)
print(f"Classification accuracy: {np.mean(scores)} / Chance level: {class_balance}")

# Test with the whole data
X_train = csp.fit_transform(epochs_data, labels_tr)
y_train = labels_tr

logR.fit(X_train, y_train)

X_test = csp.transform(epochs_data_test)
y_test = labels_ts
y_pred = logR.predict(X_test)

print(logR.score(X_solo,y_test))