import time
import uuid

import numpy as np
from matplotlib import pyplot as plt
from mne.decoding import Vectorizer
from mne.io import read_raw_fif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mne_lsl.datasets import sample
from mne_lsl.player import PlayerLSL
from mne_lsl.stream import EpochsStream, StreamLSL

fname = sample.data_path() / "mne-sample" / "sample_audvis_raw.fif"
raw = read_raw_fif(fname, preload=False).pick(("meg", "stim")).load_data()
source_id = uuid.uuid4().hex
player = PlayerLSL(raw, chunk_size=200, name="real-time-decoding", source_id=source_id)
player.start()
player.info

stream = StreamLSL(bufsize=5, name="real-time-decoding", source_id=source_id)
stream.connect(acquisition_delay=0.1, processing_flags="all")
stream.info["bads"] = ["MEG 2443"]
stream.pick(("grad", "stim")).filter(None, 40, picks="grad")
stream.info

epochs = EpochsStream(
    stream,
    bufsize=10,
    event_id=dict(audio_left=1, visual_left=3),
    event_channels="STI 014",
    tmin=-0.2,
    tmax=0.5,
    baseline=(None, 0),
    reject=dict(grad=4000e-13),  # unit: T / m (gradiometers)
).connect(acquisition_delay=0.1)
epochs.info

vectorizer = Vectorizer()
scaler = StandardScaler()
clf = LogisticRegression()
classifier = Pipeline([("vector", vectorizer), ("scaler", scaler), ("svm", clf)])

min_epochs = 10
while epochs.n_new_epochs < min_epochs:
    time.sleep(0.5)

# prepare figure to plot classifiation score
if not plt.isinteractive():
    plt.ion()
fig, ax = plt.subplots()
ax.set_xlabel("Epochsn n°")
ax.set_ylabel("Classification score (% correct)")
ax.set_title("Real-time decoding")
ax.set_xlim([min_epochs, 50])
ax.set_ylim([30, 105])
ax.axhline(50, color="k", linestyle="--", label="Chance level")
plt.show()

# decoding loop
scores_x, scores, std_scores = [], [], []
while True:
    if len(scores_x) != 0 and 50 <= scores_x[-1]:
        break
    n_epochs = epochs.n_new_epochs
    if n_epochs == 0 or n_epochs % 5 != 0:
        time.sleep(0.5)  # give time to the streaming and acquisition threads
        continue

    if len(scores_x) == 0:  # first training
        X = epochs.get_data(n_epochs=n_epochs)
        y = epochs.events[-n_epochs:]
    else:
        X = np.concatenate((X, epochs.get_data(n_epochs=n_epochs)), axis=0)
        y = np.concatenate((y, epochs.events[-n_epochs:]))
    cv = ShuffleSplit(5, test_size=0.2, random_state=42)
    scores_t = cross_val_score(classifier, X, y, cv=cv, n_jobs=1) * 100
    std_scores.append(scores_t.std())
    scores.append(scores_t.mean())
    scores_x.append(scores_x[-1] + n_epochs if len(scores_x) != 0 else n_epochs)

    # update figure
    ax.plot(scores_x[-2:], scores[-2:], "-x", color="b")
    hyp_limits = (
        np.asarray(scores[-2:]) - np.asarray(std_scores[-2:]),
        np.asarray(scores[-2:]) + np.asarray(std_scores[-2:]),
    )
    fill = ax.fill_between(
        scores_x[-2:], y1=hyp_limits[0], y2=hyp_limits[1], color="b", alpha=0.5
    )
    plt.pause(0.1)
    plt.draw()