#!/usr/bin/env python

"""
Virtual camera used to generate event log
"""

__author__ = "Kyle Long"
__email__ = "long.kyle@gmail.com"
__date__ = "09/28/2019"
__copyright__ = "Copyright 2019, Kyle Long"
__python_version__ = "3.7.4"


import datetime
import time
import random
import requests
import threading


EVENT_LOG = []
EVENTS = {'aperature adjusted to': ('f/1.2', 'f/1.4', 'f/2', 'f/2.8', 'f/4',
                                    'f/5.6', 'f/8', 'f/11', 'f/16'),
          'iso adjusted to': (100, 125, 160, 200, 250, 320, 400, 500, 640, 800,
                              1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000,
                              6400, 8000, 10000, 12800, 16000, 20000, 25600),
          'shutter speed adjusted to': ('1/25', '1/30', '1/40', '1/50', '1/60',
                                        '1/80', '1/100', '1/125', '1/160',
                                        '1/200', '1/250', '1/320', '/400',
                                        '1/500', '1/640', '1/800', '1/1000',
                                        '1/1250', '1/1600', '1/2000', '1/2500',
                                        '1/3200', '1/4000'),
          'detected motion:': ('person', 'animal', 'vehicle', 'unknown')
          }


def main():
    """
    Check to see if a camera is already running to prevent
    a race condition.
    Create and run threads.
    """
    # See if a camera is already running
    response = requests.get('http://172.18.0.2:5000/cam_running')
    if response.status_code == 403:
        message = 'Camera already running. Can not start another camera.'
        raise CameraRunningError(message)

    # Create new threads
    create_thread = CreateEventsThread()
    send_thread = SendEventsThread()

    # Start new threads
    create_thread.start()
    send_thread.start()


class CameraRunningError(Exception):
    pass


class CreateEventsThread(threading.Thread):
    """
    Add a new event to the camera's event list every 10 seconds.
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        last_event = time.time()

        while True:
            current_time = time.time()

            if (current_time - last_event) >= 10:
                log_time = datetime.datetime.now().strftime('%d-%b-%y %H:%M:%S')
                event = random.choice(list(EVENTS.keys()))
                value = random.choice(EVENTS[event])
                EVENT_LOG.append(f'{log_time}  --  {event} {value}')
                last_event = current_time


class SendEventsThread(threading.Thread):
    """
    Establish a connection with the API server.
    Send the API server the updated EVENT_LOG
    """
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):

        status_code = 0
        while True:
            # Send request to connect to API Server
            response = requests.get('http://172.18.0.2:5000/connect')
            status_code = response.status_code
            if status_code == 350:
                continue

            # send EVENT_LOG to API Server
            requests.put('http://172.18.0.2:5000/logs', json=EVENT_LOG)


if __name__ == '__main__':
    main()
