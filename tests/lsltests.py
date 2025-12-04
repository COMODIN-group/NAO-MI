import time
import uuid

import numpy as np

from mne_lsl.lsl import (
    StreamInfo,
    StreamInlet,
    StreamOutlet,
    local_clock,
    resolve_streams,
)

from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet

# Step 1: Resolve an existing LSL stream
print("Looking for an LSL stream...")
streams = resolve_stream('name','Unicorn')  # Finds available LSL streams

if not streams:
    print("No LSL stream found.")
    exit()

# Step 2: Open an inlet to receive data
inlet = StreamInlet(streams[0])
info = inlet.info()

counter = 1

chunk = list()
times = list()

while True:

    data, ts = inlet.pull_sample()

    if data:
        chunk.append(data[0:7])
        times.append(ts)

    if counter > 20:
        print(chunk)
        mat = np.array(chunk)
        print(np.transpose(mat))
        print(times)
        break

    counter += 1