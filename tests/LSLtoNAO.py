"""Example program to demonstrate how to read string-valued markers from LSL."""

from pylsl import StreamInlet, resolve_stream
import time
import subprocess

# first resolve a marker stream on the lab network
print("looking for a marker stream...")
streams = resolve_stream('name', 'OutStream')

# create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

ip = '192.168.1.101'
#ip = '172.20.10.2'
#ip = '192.168.8.106'  #router feria 
    
threshold = 0.7
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
            counter_right = 0
            if counter_left > 5:
                print('nao lifts left')
                move_command = "py -2 nao_controls.py --mode 2 --move left --ip " + ip  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)   
                counter_left = 0
                cooldown = 75
        elif sample[1] > threshold:
            print('right')
            counter_right += 1
            counter_left = 0
            if counter_right > 5:
                print('nao lifts right')
                move_command = "py -2 nao_controls.py --mode 2 --move right --ip " + ip  # launch your python2 script
                process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
                counter_right = 0
                cooldown = 75
        else:
            print('Not sure')
            counter_left = 0
            counter_right = 0
    else:
        cooldown -= 1



