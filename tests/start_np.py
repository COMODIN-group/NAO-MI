import requests
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = requests.get('http://127.0.0.1:6937/executions')

if r.status_code not in [200, 201]:
    print('Could not reach Neuropype! Please ensure it is running')
    exit()

#New id for execution
r = requests.post('http://127.0.0.1:6937/executions', json={})

execution_id = r.json()['id']

URL = 'http://127.0.0.1:6937/executions/' + str(execution_id)

#Set path to pipeline
rootpath = ''
rootpath = os.path.abspath(os.path.expanduser(rootpath))
pipepath = os.path.join(rootpath, 'NaoPSD.pyp')

#Load the pipeline
requests.post(URL + '/actions/load', json={'file': pipepath, 'what': 'graph'})
logger.info(f'Lauching pipeline: {pipepath}')

#Start the pipeline execution
requests.patch(URL + '/state', json={'running': True, 'paused': False})

#Pause execution
#requests.patch(URL + '/state', json={'paused': True})

#Resume
#requests.patch(URL + '/state', json={'paused': False})

#Stop
#requests.patch(URL + '/state', json={'running': False})

#Restart
#requests.patch(URL + '/state', json={'running': True})

#Delete
#r.delete(URL)
