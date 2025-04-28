import threading
import time
import json
import socketio
from cortex import Cortex
from pylsl import StreamInfo, StreamOutlet
import pylsl
from dotenv import load_dotenv
import os
from utilities import * 
import math
import psycopg2

# load .env environment variables
load_dotenv('.env')

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
UI_HOST = os.getenv("UI_HOST")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SOCKET_SERVER_URL = os.getenv("SOCKET_SERVER_URL")
eeg_cols = ["event_time","unix_timestamp","lsl_timestamp","round_id", "player_id", "uid", "labels", "eeg_data"]

# Socket.IO client to connect to remote server
sio = socketio.Client()

class Subcribe:
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_eeg_data=self.on_new_eeg_data)
        self.c.bind(new_met_data=self.on_new_met_data)
        self.c.bind(inform_error=self.on_inform_error)

        self.session_ready = threading.Event()
        self.eeg_outlet = None
        self.met_outlet = None
        self.eeg_labels = []
        self.met_labels = []
        self.streaming = False
        self.current_metadata = {}
        self.buffer = []
        self.player_id = None
        self.round_id = None
        self.uid = None

    def connect(self, headsetId=''):
        if headsetId:
            self.c.set_wanted_headset(headsetId)
        self.c.open()

    def on_create_session_done(self, *args, **kwargs):
        print('[Session] Ready')
        self.session_ready.set()

    def start_streaming(self, player_id, round_id, uid):
        print(f"[Streaming] Starting for player: {player_id}, uid: {uid}, round: {round_id}")
        self.current_metadata = {'player_id': player_id, 'uid': uid, 'round_id': round_id, 'start_time': time.time()}
        self.buffer = []
        self.streaming = True
        self.debug = True
        self.c.sub_request(['eeg', 'met'])

    def stop_streaming(self):
        print("[Streaming] Stopping and saving data")
        self.streaming = False
        self.c.unsub_request(['eeg', 'met'])
        self.current_metadata['end_time'] = time.time()
        self.current_metadata['data'] = self.buffer

        fname = f"jsonlogs/eeg_met_{self.current_metadata['uid']}_{self.current_metadata['player_id']}_round_{self.current_metadata['round_id']}.json"
        with open(fname, 'w') as f:
            json.dump(self.current_metadata, f)
        print(f"[Saved] Data saved to {fname}")

    def close_connection(self):
        print("[Connection] Closing session")
        self.c.close()

    def on_new_data_labels(self, *args, **kwargs):
        data = kwargs.get('data')
        stream_name = data['streamName']
        labels = data['labels']

        if stream_name == 'eeg':
            self.eeg_labels = labels
            # info = StreamInfo(name='Emotiv_EEG', type='EEG',
            #                   channel_count=1, nominal_srate=256,
            #                   channel_format=pylsl.cf_string, source_id='emotiv')
            # self.eeg_outlet = StreamOutlet(info)
            # print('[LSL] EEG outlet created')

        elif stream_name == 'met':
            self.met_labels = labels
            # info = StreamInfo(name='Emotiv_MET', type='MET',
            #                   channel_count=1, nominal_srate=0.1,
            #                   channel_format=pylsl.cf_string, source_id='emotiv')
            # self.met_outlet = StreamOutlet(info)
            # print('[LSL] MET outlet created')

    def on_new_eeg_data(self, *args, **kwargs):
        # print("self.streaming ", self.streaming)
        if not self.streaming:
            return
        data = kwargs.get('data')
        sample = data['eeg']
        timestamp = data['time']

        sample_obj = {}
        sample_obj["timestamp"] = timestamp
        sample_obj["player_id"] = self.player_id
        sample_obj["round_id"] = self.round_id
        sample_obj["uid"] = self.uid
        sample_obj["type"] = 'eeg'
        sample_obj["labels"] = self.eeg_labels
        sample_obj["data"] = sample

        eeg_cols = ["event_time","unix_timestamp","lsl_timestamp","round_id", "player_id", "uid", "labels", "eeg_data"]

        try:
            if conn:
                insert_row(conn,
                schema="public",
                table="eeg_data",
                columns=eeg_cols,
                data=(
                        timestamp,
                        time.time(),
                        pylsl.local_clock(),
                        self.round_id,
                        self.player_id,
                        self.uid,
                        self.eeg_labels,
                        sample
                ))
        except Exception as e: 
            print("Error saving to eeg_data: ", e) 

        try:
            if self.eeg_outlet:
                sample_str = json.dumps(sample_obj)
                self.eeg_outlet.push_sample([sample_str])
                
            # print('LSL eeg data: {}'.format([sample_str]))
            # print('eeg data: {}'.format(data))
            self.buffer.append(sample_obj)
        except Exception as e:
            print("EEG Error {}".format(e))   
    
    def on_new_met_data(self, *args, **kwargs):
        # print("self.streaming ", self.streaming)
        if not self.streaming:
            return
        data = kwargs.get('data')
        sample = data['met']
        timestamp = data['time']

        sample_obj = {}
        sample_obj["timestamp"] = timestamp
        sample_obj["player_id"] = self.player_id
        sample_obj["round_id"] = self.round_id
        sample_obj["uid"] = self.uid
        sample_obj["type"] = 'met'
        sample_obj["labels"] = self.met_labels
        sample_obj["data"] = sample
        print("org sample ", sample)
        converted_sample = prepare_met_array(sample)
        print("===.converted_sample ", converted_sample)
        metrics_cols = ["event_time","unix_timestamp","lsl_timestamp","round_id", "player_id", "uid", "labels", "metrics_data"]
        
        try:
            if conn:
                insert_row(conn,
                schema="public",
                table="metrics_data",
                columns=metrics_cols,
                data=(
                        timestamp,
                        time.time(),
                        pylsl.local_clock(),
                        self.round_id,
                        self.player_id,
                        self.uid,
                        self.met_labels,
                        converted_sample
                ))
        except Exception as e: 
            print("Error saving to metrics_data: ", e) 

        try:
            if self.met_outlet:
                sample_str = json.dumps(sample_obj)
                self.met_outlet.push_sample([sample_str])
            print('met data: {}'.format(data))
            self.buffer.append(sample_obj)
        except Exception as e:
            print("MET Error {}".format(e))

    def on_inform_error(self, *args, **kwargs):
        print('[Error]', kwargs.get('error_data'))


sub_instance = None


@sio.event
def connect():
    # load_dotenv(dotenv_path='.env')

    print("[SocketIO] Connected to server")
    global sub_instance
 
    # Please fill your application clientId and clientSecret before running script
    your_app_client_id = CLIENT_ID
    your_app_client_secret = CLIENT_SECRET
    print(your_app_client_id, your_app_client_secret)

    sub_instance = Subcribe(your_app_client_id, your_app_client_secret)
    threading.Thread(target=sub_instance.connect, daemon=True).start()
    while not sub_instance.session_ready.is_set():
        time.sleep(0.1)
    print("[Cortex] Session ready")

@sio.event
def disconnect():
    print("[SocketIO] Disconnected from server")

@sio.on('start_ecg')
def handle_start_ecg(data):
    start_info = data.get('start_info')
    player_id = start_info.get('player_id')
    round_id = start_info.get('round_id')
    uid = start_info.get('uid')
    global sub_instance
    sub_instance.player_id = player_id
    sub_instance.round_id = round_id
    sub_instance.uid = uid
    if sub_instance:
        sub_instance.start_streaming(player_id, round_id, uid)

@sio.on('stop_ecg')
def handle_stop_ecg(data):
    if sub_instance:
        sub_instance.stop_streaming()

@sio.on('end_connection')
def handle_end_connection():
    global sub_instance
    if sub_instance:
        sub_instance.close_connection()
        sub_instance = None

global conn
conn = None
def main():
    # load_dotenv(dotenv_path='.env')
    # socket_server_url = os.getenv("SOCKET_SERVER_URL")
    print(f"[Client] Connecting to Socket.IO server at {SOCKET_SERVER_URL}")
    sio.connect(SOCKET_SERVER_URL)
    # sio.wait()

    # Connect database
    try:
        global conn
        conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
        )
        print("Database connected.")
    except Exception as e:
        print(f"Unable to establish a connection with database hosted on {DB_HOST}. Exception: {e}")

    try:
        info = StreamInfo(name='Emotiv_EEG', type='EEG',
                              channel_count=1, nominal_srate=256,
                              channel_format=pylsl.cf_string, source_id='emotiv')
        sub_instance.eeg_outlet = StreamOutlet(info)
        print('[LSL] EEG outlet created')
        info = StreamInfo(name='Emotiv_MET', type='MET',
                              channel_count=1, nominal_srate=0.1,
                              channel_format=pylsl.cf_string, source_id='emotiv')
        sub_instance.met_outlet = StreamOutlet(info)
        print('[LSL] MET outlet created')
    except Exception as e:
        print(f"[LSL] Exception: {e}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Main] Exiting on user interrupt.")
        handle_stop_ecg({})
        handle_end_connection()


import keyboard

if __name__ == '__main__':
    main()

    if keyboard.is_pressed("esc"):
        handle_stop_ecg({})
        handle_end_connection()

 