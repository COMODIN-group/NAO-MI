import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from pylsl import StreamInlet, resolve_stream

import requests
import logging
import os
import threading
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AplicacionTkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("NAO_MI GUI")
        self.root.geometry("300x700+1000+40")
        self.server = False
        self.running = False

        b1_style = ttk.Style()
        b1_style.configure('TButton', font =
               ('calibri', 10),
                    borderwidth = '4')
        b1_style.map('TButton', foreground = [('active', '!disabled', 'blue')],
                     background = [('active', 'black')])

        b2_style = ttk.Style()
        b2_style.configure('B2.TButton', font =
            ('calibri', 10),
            borderwidth = '3')
        b2_style.map('B2.TButton', foreground = [('active', '!disabled', 'green')],
                    background = [('active', 'black')])

        b3_style = ttk.Style()
        b3_style.configure('B3.TButton', font =
            ('calibri', 10),
            borderwidth = '3')
        b3_style.map('B3.TButton', foreground = [('active', '!disabled', 'red')],
                    background = [('active', 'black')])

        self.print_style_L = ttk.Style()
        self.print_style_L.configure('L.TLabel', font = ('calibri', 15),  foreground = 'blue')

        self.print_style_R = ttk.Style()
        self.print_style_R.configure('R.TLabel', font = ('calibri', 15), foreground = 'red')

        self.print_style_cool = ttk.Style()
        self.print_style_cool.configure('C.TLabel', font = ('calibri', 15))

        img = ImageTk.PhotoImage(Image.open("naomi_logo.png").resize((225,157)))
        panel = ttk.Label(root, image = img)
        panel.image = img
        panel.pack(side = "top")
        
        frame_pipe = tk.Frame(root)
        frame_pipe.pack(pady=10)

        start_button = ttk.Button(frame_pipe, text='Start Pipeline',style='TButton',command =lambda: self.np_server('start'))
        start_button.grid(row=0, column=0, columnspan=2, pady=5)

        pause_button = ttk.Button(frame_pipe, text='Pause',style='TButton',command =lambda: self.np_server('pause'))
        pause_button.grid(row=1, column=0, padx=10, pady=5)

        resume_button = ttk.Button(frame_pipe, text='Resume',style='TButton',command =lambda: self.np_server('resume'))
        resume_button.grid(row=1, column=1, padx=10, pady=5)

        frame_nao = tk.Frame(root)
        frame_nao.pack(pady=5)

        startNAO_button = ttk.Button(frame_nao, text='Start NAO',style='B2.TButton',command = self.start_LSL)
        startNAO_button.grid(row=0, column=0, columnspan=2, pady=5)

        pause_button = ttk.Button(frame_nao, text='Pause',style='B2.TButton',command = self.stop_LSL)
        pause_button.grid(row=1, column=0, padx=10, pady=5)

        resume_button = ttk.Button(frame_nao, text='Resume',style='B2.TButton',command = self.start_LSL)
        resume_button.grid(row=1, column=1, padx=10, pady=5)

        # Frame para entrada de texto
        frame_cooldown = ttk.Frame(root)
        frame_cooldown.pack(pady=10, padx=10)
        ttk.Label(frame_cooldown, text="Cooldown Time :").pack(side="left", padx=5)
        self.entry_var = tk.StringVar(value="100")
        self.cooldown_input = ttk.Entry(frame_cooldown,  textvariable=self.entry_var)
        self.cooldown_input.pack(side="left", fill="x", expand=True)

        frame_slider = ttk.Frame(root)
        frame_slider.pack(pady=10, padx=10)
        ttk.Label(frame_slider, text="Threshold Right:").grid(row=0, column=1, padx=5, pady=5)
        self.slider_right = tk.Scale(frame_slider,from_=0, to=1, resolution=0.1, orient="horizontal")
        self.slider_right.set(0.5)
        self.slider_right.grid(row=1, column=1, padx=5, pady=5)

        #Slider left
        ttk.Label(frame_slider, text="Threshold Left:").grid(row=0, column=0, padx=5, pady=5)
        self.slider_left = tk.Scale(frame_slider, from_=0, to=1, resolution=0.1, orient="horizontal")
        self.slider_left.set(0.5)
        self.slider_left.grid(row=1, column=0, padx=5, pady=5)

        # Pantalla de salida
        self.param_text = tk.StringVar()
        self.param_text.set(f"Cooldown: {self.cooldown_input.get()} | Threshold: {float(self.slider_left.get()):.1f} / {float(self.slider_right.get()):.1f}")
        ttk.Label(root, textvariable=self.param_text, wraplength=380).pack(pady=5)

        update_button = ttk.Button(root, text="Update parameters", command= self.update_LSL)
        update_button.pack(pady=15)

        frame_print = ttk.Frame(root)
        frame_print.pack(pady=10, padx=10)

        ttk.Label(frame_print, text="Right", style = 'R.TLabel').grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(frame_print, text="Left", style = 'L.TLabel').grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(frame_print, text="Cooldown", style = 'C.TLabel').grid(row=0, column=1, padx=5, pady=5)

        exit_button = ttk.Button(root, text='Exit', style='B3.TButton',command = self.close_all)
        exit_button.pack(pady=15)

    def update_parameters(self):
        self.salida_texto.set(f"Cooldown: {self.cooldown_input.get()} | Threshold: {float(self.slider_left.get()):.1f} / {float(self.slider_right.get()):.1f}")

    def np_server(self, state):

        r = requests.get('http://127.0.0.1:6937/executions')

        if r.status_code not in [200, 201]:
            print('Could not reach Neuropype! Please ensure it is running')
            exit()

        match state:
            case 'start':
                #New id for execution
                self.r = requests.post('http://127.0.0.1:6937/executions', json={})

                self.execution_id = self.r.json()['id']

                self.URL = 'http://127.0.0.1:6937/executions/' + str(self.execution_id)

                self.server = True

                #Set path to pipeline
                rootpath = ''
                rootpath = os.path.abspath(os.path.expanduser(rootpath))
                pipepath = os.path.join(rootpath, 'neuropype/NaoPSD.pyp')

                #Load the pipeline
                requests.post(self.URL + '/actions/load', json={'file': pipepath, 'what': 'graph'})
                logger.info(f'Lauching pipeline: {pipepath}')

                #Start the pipeline execution
                requests.patch(self.URL + '/state', json={'running': True, 'paused': False})

            case 'pause':
                #Pause execution
                requests.patch(self.URL + '/state', json={'paused': True})
            case 'resume':
                #Resume
                requests.patch(self.URL + '/state', json={'paused': False})
            case 'stop':
                #Stop
                requests.patch(self.URL + '/state', json={'running': False})
                #Delete
                requests.delete(self.URL)

                self.server = False

    def start_LSL(self):

        self.t = threading.Thread(target=self.LSLtoNAO)
        self.t.start()

    def stop_LSL(self):

        self.running = False

    def update_LSL(self):

        self.param_text.set(f"Cooldown: {self.cooldown_input.get()} | Threshold: {float(self.slider_left.get()):.1f} / {float(self.slider_right.get()):.1f}")
        self.stop_LSL()
        time.sleep(2)
        self.start_LSL()

    def LSLtoNAO(self):

        # first resolve a marker stream on the lab network
        streams = resolve_stream('name', 'OutStreams')

        # create a new inlet to read from the stream
        inlet = StreamInlet(streams[0])

        ip = '192.168.1.101' #router nao
        #ip = '192.168.8.106'  #router feria 

        self.running = True

        threshold_right = self.slider_right.get()
        threshold_left = self.slider_left.get()
        cooldown_time = int(self.entry_var.get())

        cooldown = 0
        counter_right = 0
        counter_left = 0

        while self.running:
            # get a new sample (you can also omit the timestamp part if you're not
            # interested in it)
            sample,timestamp = inlet.pull_sample()
            
            if cooldown == 0:
                if sample[0] >= threshold_left:
                    print('left')
                    counter_left += 1
                    counter_right = 0
                    if counter_left > 3:
                        print('nao lifts left')
                        #self.update_cmd('nao lifts left')
                        #move_command = "py -2 nao_controls.py --mode 2 --move left --ip " + ip  # launch your python2 script
                        #process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)   
                        counter_left = 0
                        cooldown = cooldown_time
                elif sample[0] <= -threshold_right:
                    print('right')
                    counter_right += 1
                    counter_left = 0
                    if counter_right > 3:
                        print('nao lifts right')
                        #move_command = "py -2 nao_controls.py --mode 2 --move right --ip " + ip  # launch your python2 script
                        #process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE, text = True)
                        counter_right = 0
                        cooldown = cooldown_time
                else:
                    #self.update_cmd('...cooling down...')
                    counter_left = 0
                    counter_right = 0
            else:
                print('..cooling down...')
                cooldown -= 1


    def close_all(self):

        if self.running == True:
            self.stop_LSL()

        if self.server == True:
            self.np_server('stop')
        
        self.root.destroy()
    

def main():
    root = tk.Tk()
    app = AplicacionTkinter(root)
    root.mainloop()

if __name__ == "__main__":
    main()