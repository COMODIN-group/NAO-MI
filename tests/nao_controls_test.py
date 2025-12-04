
import subprocess

ip = '192.168.1.101'
#ip = '172.20.10.2'
#ip = '192.168.8.106' 

move_command = "py -2 nao_controls.py --mode 2 --move left --ip " + ip  # launch your python2 script
process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)   