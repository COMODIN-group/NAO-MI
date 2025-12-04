import time
import uuid

import numpy as np
from matplotlib import pyplot as plt

import mne
from mne.decoding import Vectorizer
from mne.io import read_raw_eeglab

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import ShuffleSplit, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mne_lsl.datasets import sample
from mne_lsl.player import PlayerLSL
from mne_lsl.stream import EpochsStream, StreamLSL

from mne_lsl.lsl import (
    StreamInfo,
    StreamInlet,
    StreamOutlet,
    local_clock,
    resolve_streams,
)

raw = read_raw_eeglab('MI_merged_train.set', preload = 'True')

event_id = {"right": 1, "left": 2, "both": 3} 

events, event_dict = mne.events_from_annotations(raw, event_id)

tmin, tmax = -1.0, 4.0

epochs = Epochs(
    raw,
    event_id=["right", "left"],
    tmin=tmin,
    tmax=tmax,
    proj=True,
    picks=picks,
    baseline=None,
    preload=True,
)

epochs_train = epochs.copy().crop(tmin=1.0, tmax=2.0)
labels = epochs.events[:, -1] - 2

source_id = uuid.uuid4().hex
player = PlayerLSL(raw, chunk_size=1, name="lsltest", source_id=source_id)
player.start()
player.info

streams = resolve_streams()
streams[0]

inlet = StreamInlet(streams[0])
inlet.open_stream()

epochs = EpochsStream(
    inlet,
    bufsize=10,
    event_id=event_dict,

    tmin=-0.2,
    tmax=0.5,
    baseline=(None, 0)
).connect(acquisition_delay=0.1)

epochs.info


while True:

    sample, timestamp = inlet.pull_sample()
    if sample.any():
        print(sample, timestamp)