from cortex import Cortex
from dotenv import load_dotenv
# import socket
# import threading
import time

# from dotenv import load_dotenv
import os

class Subcribe():
    """
    A class to subscribe data stream.

    Attributes
    ----------
    c : Cortex
        Cortex communicate with Emotiv Cortex Service

    Methods
    -------
    start():
        start data subscribing process.
    sub(streams):
        To subscribe to one or more data streams.
    on_new_data_labels(*args, **kwargs):
        To handle data labels of subscribed data 
    on_new_eeg_data(*args, **kwargs):
        To handle eeg data emitted from Cortex
    on_new_mot_data(*args, **kwargs):
        To handle motion data emitted from Cortex
    on_new_dev_data(*args, **kwargs):
        To handle device information data emitted from Cortex
    on_new_met_data(*args, **kwargs):
        To handle performance metrics data emitted from Cortex
    on_new_pow_data(*args, **kwargs):
        To handle band power data emitted from Cortex
    """
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        """
        Constructs cortex client and bind a function to handle subscribed data streams
        If you do not want to log request and response message , set debug_mode = False. The default is True
        """
        print("Subscribe __init__")
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_eeg_data=self.on_new_eeg_data)
        self.c.bind(new_mot_data=self.on_new_mot_data)
        self.c.bind(new_dev_data=self.on_new_dev_data)
        self.c.bind(new_met_data=self.on_new_met_data)
        self.c.bind(new_pow_data=self.on_new_pow_data)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, streams, headsetId=''):
        """
        To start data subscribing process as below workflow
        (1)check access right -> authorize -> connect headset->create session
        (2) subscribe streams data
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power
        'eq' : EEQ Quality

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']
        headsetId: string , optional
             id of wanted headet which you want to work with it.
             If the headsetId is empty, the first headset in list will be set as wanted headset
        Returns
        -------
        None
        """
        self.streams = streams

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def sub(self, streams):
        """
        To subscribe to one or more data streams
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']

        Returns
        -------
        None
        """
        self.c.sub_request(streams)

    def unsub(self, streams):
        """
        To unsubscribe to one or more data streams
        'eeg': EEG
        'mot' : Motion
        'dev' : Device information
        'met' : Performance metric
        'pow' : Band power

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['eeg', 'mot']

        Returns
        -------
        None
        """
        self.c.unsub_request(streams)

    def on_new_data_labels(self, *args, **kwargs):
        """
        To handle data labels of subscribed data 
        Returns
        -------
        data: list  
              array of data labels
        name: stream name
        For example:
            eeg: ["COUNTER","INTERPOLATED", "AF3", "T7", "Pz", "T8", "AF4", "RAW_CQ", "MARKER_HARDWARE"]
            motion: ['COUNTER_MEMS', 'INTERPOLATED_MEMS', 'Q0', 'Q1', 'Q2', 'Q3', 'ACCX', 'ACCY', 'ACCZ', 'MAGX', 'MAGY', 'MAGZ']
            dev: ['AF3', 'T7', 'Pz', 'T8', 'AF4', 'OVERALL']
            met : ['eng.isActive', 'eng', 'exc.isActive', 'exc', 'lex', 'str.isActive', 'str', 'rel.isActive', 'rel', 'int.isActive', 'int', 'foc.isActive', 'foc']
            pow: ['AF3/theta', 'AF3/alpha', 'AF3/betaL', 'AF3/betaH', 'AF3/gamma', 'T7/theta', 'T7/alpha', 'T7/betaL', 'T7/betaH', 'T7/gamma', 'Pz/theta', 'Pz/alpha', 'Pz/betaL', 'Pz/betaH', 'Pz/gamma', 'T8/theta', 'T8/alpha', 'T8/betaL', 'T8/betaH', 'T8/gamma', 'AF4/theta', 'AF4/alpha', 'AF4/betaL', 'AF4/betaH', 'AF4/gamma']
        """
        data = kwargs.get('data')
        stream_name = data['streamName']
        stream_labels = data['labels']
        print('{} labels are : {}'.format(stream_name, stream_labels))

    def on_new_eeg_data(self, *args, **kwargs):
        """
        To handle eeg data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array eeg match the labels in the array labels return at on_new_data_labels
        For example:
           {'eeg': [99, 0, 4291.795, 4371.795, 4078.461, 4036.41, 4231.795, 0.0, 0], 'time': 1627457774.5166}
        """
        data = kwargs.get('data')
        print('eeg data: {}'.format(data))

    def on_new_mot_data(self, *args, **kwargs):
        """
        To handle motion data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array motion match the labels in the array labels return at on_new_data_labels
        For example: {'mot': [33, 0, 0.493859, 0.40625, 0.46875, -0.609375, 0.968765, 0.187503, -0.250004, -76.563667, -19.584995, 38.281834], 'time': 1627457508.2588}
        """
        data = kwargs.get('data')
        print('motion data: {}'.format(data))

    def on_new_dev_data(self, *args, **kwargs):
        """
        To handle dev data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array dev match the labels in the array labels return at on_new_data_labels
        For example:  {'signal': 1.0, 'dev': [4, 4, 4, 4, 4, 100], 'batteryPercent': 80, 'time': 1627459265.4463}
        """
        data = kwargs.get('data')
        print('dev data: {}'.format(data))

    def on_new_met_data(self, *args, **kwargs):
        """
        To handle performance metrics data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array met match the labels in the array labels return at on_new_data_labels
        For example: {'met': [True, 0.5, True, 0.5, 0.0, True, 0.5, True, 0.5, True, 0.5, True, 0.5], 'time': 1627459390.4229}
        """
        data = kwargs.get('data')
        print('pm data: {}'.format(data))

    def on_new_pow_data(self, *args, **kwargs):
        """
        To handle band power data emitted from Cortex

        Returns
        -------
        data: dictionary
             The values in the array pow match the labels in the array labels return at on_new_data_labels
        For example: {'pow': [5.251, 4.691, 3.195, 1.193, 0.282, 0.636, 0.929, 0.833, 0.347, 0.337, 7.863, 3.122, 2.243, 0.787, 0.496, 5.723, 2.87, 3.099, 0.91, 0.516, 5.783, 4.818, 2.393, 1.278, 0.213], 'time': 1627459390.1729}
        """
        data = kwargs.get('data')
        print('pow data: {}'.format(data))

    # callbacks functions
    def on_create_session_done(self, *args, **kwargs):
        print('on_create_session_done')

        # subribe data 
        self.sub(self.streams)

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(error_data)

# -----------------------------------------------------------
# 
# GETTING STARTED
#   - Please reference to https://emotiv.gitbook.io/cortex-api/ first.
#   - Connect your headset with dongle or bluetooth. You can see the headset via Emotiv Launcher
#   - Please make sure the your_app_client_id and your_app_client_secret are set before starting running.
#   - In the case you borrow license from others, you need to add license = "xxx-yyy-zzz" as init parameter
# RESULT
#   - the data labels will be retrieved at on_new_data_labels
#   - the data will be retreived at on_new_[dataStream]_data
# 
# -----------------------------------------------------------


# # Include the Subcribe class above here...

# HOST = '127.0.0.1'
# PORT = 65432
# streams = ['eeg', 'eq', 'met', 'pow']
# sub_instance = None  # Global reference to Subcribe instance

# def socket_server():
#     global sub_instance
#     print(f"[Socket] Listening on {HOST}:{PORT}")
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind((HOST, PORT))
#         s.listen()
#         conn, addr = s.accept()
#         with conn:
#             print(f"[Socket] Connected by {addr}")
#             while True:
#                 msg = conn.recv(1024).decode().strip()
#                 print(f"[Socket] Received: {msg}")

#                 if msg == "start_ecg":
#                     if sub_instance is None:
#                         print("[Socket] Initializing Cortex connection...")
#                         sub_instance = Subcribe(your_app_client_id, your_app_client_secret)
#                         threading.Thread(target=sub_instance.start, args=(streams,), daemon=True).start()
#                     else:
#                         print("[Socket] Cortex connection already started.")

#                 elif msg == "stop_ecg":
#                     if sub_instance:
#                         print("[Socket] Stopping stream...")
#                         sub_instance.unsub(streams)
#                         sub_instance = None  # Clean up for next round
#                         break
#                 elif msg == "":
#                     break

# def main():
#     global your_app_client_id, your_app_client_secret
    
#     CLIENT_ID = os.getenv("CLIENT_ID")
#     CLIENT_SECRET = os.getenv("CLIENT_SECRET")
#     # Please fill your application clientId and clientSecret before running script
#     your_app_client_id = CLIENT_ID
#     your_app_client_secret = CLIENT_SECRET


#     listener_thread = threading.Thread(target=socket_server, daemon=True)
#     listener_thread.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("[Main] Exiting on user interrupt.")

# if __name__ == '__main__':
#     main()
 


def main():

    load_dotenv(dotenv_path='.env')

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    # Please fill your application clientId and clientSecret before running script
    your_app_client_id = CLIENT_ID
    your_app_client_secret = CLIENT_SECRET

    s = Subcribe(your_app_client_id, your_app_client_secret)

    # list data streams
    streams = ['eeg','eq','met','pow']
    s.start(streams)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Main] Exiting on user interrupt.")

if __name__ =='__main__':
    main()

# -----------------------------------------------------------
