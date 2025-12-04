#NAO_calibration

from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
import numpy as np
import subprocess

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

eeg_outlet = StreamOutlet(outlet_info)

marker_info = StreamInfo('MyMarkerStream', 'Markers', 1, 0, 'string', 'markers1234')

# next make an outlet
marker_outlet = StreamOutlet(marker_info)

print("Relaying data with labeled channels...")
print("Sending markers...")

markernames = ['left','right','left','right','left','right','left','right','left','right']

sample_counter = 1
last_sample = 1

counter = 0
calibration = True

ip = '192.168.1.101' #wifi_nao
#ip = '172.20.10.2' #iphone

while True:
    sample, timestamp = inlet.pull_sample()
    if sample:
        eeg_outlet.push_sample(sample)

    if calibration:
        if sample_counter == sfreq * 5:
            marker_outlet.push_sample(['begin_calib'])
            print('begin')
            last_sample = sample_counter

        if sample_counter - last_sample == sfreq * 6:
            try:
                mov = markernames[counter]
                if mov == 'left':
                    print('nao lifts left')
                    marker_outlet.push_sample(['left'])
                    move_command = "py -2 nao_controls.py --mode 2 --move left --ip " + ip
                    process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text=True)   
                    counter += 1
                    last_sample = sample_counter
                else:
                    print('nao lifts right')
                    marker_outlet.push_sample(['right'])
                    move_command = "py -2 nao_controls.py --mode 2 --move right --ip " + ip
                    process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text=True) 
                    counter += 1
                    last_sample = sample_counter
            except:
                marker_outlet.push_sample(['end_calib'])
                print('end')
                calibration = False

    sample_counter += 1


