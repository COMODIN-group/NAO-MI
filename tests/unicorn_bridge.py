from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
import numpy as np

# Step 1: Resolve an existing LSL stream
print("Looking for an LSL stream...")
streams = resolve_stream('name','Unicorn')  # Finds available LSL streams

if not streams:
    print("No LSL stream found.")
    exit()

# Step 2: Open an inlet to receive data
inlet = StreamInlet(streams[0])
info = inlet.info()

# Get stream details
name = info.name()
sfreq = info.nominal_srate()
channel_count = info.channel_count()

print(f"Connected to stream: {name}, Sampling Rate: {sfreq}, Channels: {channel_count}")

# Step 4: Create a new LSL outlet stream
outlet_info = StreamInfo('RelayedStream', 'EEG', channel_count, sfreq, 'float32', 'relay1234')
outlet_info.desc().append_child_value("source", name)

#Intento de nombrar los canales, canales y localizaciones erroneas
channel_names = ['FC1', 'FCz', 'FC2', 'C3', 'C4', 'CP1', 'CPz', 'CP2', 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']
n_channels = len(channel_names)

chns = outlet_info.desc().append_child("channels")
for chan_ix, label in enumerate(channel_names):
    ch = chns.append_child("channel")
    ch.append_child_value("label", label)
    ch.append_child_value("unit", "microvolts")
    ch.append_child_value("type", "EEG")

outlet = StreamOutlet(outlet_info)
    
print("Relaying data with labeled channels...")

while True:
    sample, timestamp = inlet.pull_sample()
    if sample:
        outlet.push_sample(sample, timestamp)
