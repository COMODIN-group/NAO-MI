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

cv = ShuffleSplit(5, test_size=0.10, random_state=42)
cv_split = cv.split(epochs_data_train)

# Assemble a classifier
vectorizer = Vectorizer()
scaler = StandardScaler()
logR = LogisticRegression()
lda = LinearDiscriminantAnalysis()
csp = CSP(n_components=8, reg=None, log=True, norm_trace=False)

# Use scikit-learn Pipeline with cross_val_score function
clf = Pipeline([("CSP", csp), ("lda",lda)])
scores = cross_val_score(clf, epochs_data_train, labels_tr, cv=cv, n_jobs=None)

# Printing the results
class_balance = np.mean(labels_tr == labels_tr[0])
class_balance = max(class_balance, 1.0 - class_balance)
print(scores)
print(f"Classification accuracy: {np.mean(scores)} / Chance level: {class_balance}")

# plot CSP patterns estimated on full data for visualization
csp.fit_transform(epochs_data, labels_tr)

csp.plot_patterns(epochs_tr.info, ch_type="eeg", units="Patterns (AU)", size=1.5)

sfreq = raw_train.info["sfreq"]
w_length = int(sfreq * 0.5)  # running classifier: window length
w_step = int(sfreq * 0.1)  # running classifier: window step size
w_start = np.arange(0, epochs_data.shape[2] - w_length, w_step)

scores_windows = []

for train_idx, test_idx in cv_split:
    y_train, y_test = labels_tr[train_idx], labels_tr[test_idx]

    X_train = csp.fit_transform(epochs_data_train[train_idx], y_train)
    X_test = csp.transform(epochs_data_train[test_idx])

    # fit classifier
    lda.fit(X_train, y_train)

    # running classifier: test classifier on sliding window
    score_this_window = []
    for n in w_start:
        X_test = csp.transform(epochs_data[test_idx][:, :, n : (n + w_length)])
        score_this_window.append(lda.score(X_test, y_test))
    scores_windows.append(score_this_window)

# Plot scores over time
w_times = (w_start + w_length / 2.0) / sfreq + epochs_tr.tmin

plt.figure()
plt.plot(w_times, np.mean(scores_windows, 0), label="Score")
plt.axvline(0, linestyle="--", color="k", label="Onset")
plt.axhline(0.5, linestyle="-", color="k", label="Chance")
plt.xlabel("time (s)")
plt.ylabel("classification accuracy")
plt.title("Classification score over time")
plt.legend(loc="lower right")
plt.show()
