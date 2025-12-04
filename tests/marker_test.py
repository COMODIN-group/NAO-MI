#NAO_calibration

from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
import numpy as np
import subprocess
import time

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
sfreq = 250 

ip = '192.168.1.101' #wifi_nao
#ip = '172.20.10.2' #iphone

while calibration:

    if sample_counter == sfreq * 5:
        time.sleep(5)
        marker_outlet.push_sample(['begin_calib'])
        print('begin')
        last_sample = sample_counter
        time.sleep(5)

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
            time.sleep(6)
        except:
            marker_outlet.push_sample(['end_calib'])
            print('end')
            calibration = False

    sample_counter += 1 

# first resolve a marker stream on the lab network
print("looking for a marker stream...")
streams = resolve_stream('name', 'OutStream')

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

threshold = 0.6
counter_left = 0
counter_right = 0
cooldown = 0

while True:
    # get a new sample (you can also omit the timestamp part if you're not
    # interested in it)
    sample,timestamp = inlet.pull_sample()
    print("got %s at time %s" % (sample, timestamp))

    if cooldown == 0:
        if sample[0] > threshold:
            print('left')
            counter_left += 1
            if counter_left > 5:
                print('nao lifts left')
                move_command = "py -2 nao_controls.py --mode 2 --move left --ip " + ip  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)   
                counter_left = 0
                cooldown = 100
        elif sample[1] > threshold:
            print('right')
            counter_right += 1
            if counter_right > 5:
                print('nao lifts right')
                move_command = "py -2 nao_controls.py --mode 2 --move right --ip " + ip  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
                counter_right = 0
                cooldown = 100
        else:
            print('Not sure')
            counter_left = 0
            counter_right = 0
    else:
        cooldown -= 1



