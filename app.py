#!/usr/bin/env python

"""
API web server that the camera and a web client can both access
using standard REST APIs
"""

__author__ = "Kyle Long"
__email__ = "long.kyle@gmail.com"
__date__ = "09/28/2019"
__copyright__ = "Copyright 2019, Kyle Long"
__python_version__ = "3.7.4"


from flask import Flask, jsonify, make_response, request
import time

app = Flask(__name__)

EVENTS = []
GET_REQUEST = False
RETURN_EVENTS = False
CAM_RUNNING = False


@app.route('/cam_running', methods=['GET'])
def cam_running():
    """
    Check to see if a camera is already running
    """
    # Check twice just to make sure we didn't catch this RIGHT when
    # we were establishing a fresh camera connection with the server
    cam_run1 = CAM_RUNNING
    time.sleep(0.5)
    cam_run2 = CAM_RUNNING

    if cam_run1 is cam_run2 is True:
        code = 403
        json_message = jsonify({"Forbidden": "Camera already running"})
    else:
        code = 200
        json_message = jsonify({"Approved": "No cameras running"})

    return make_response(json_message, code)


@app.route('/connect', methods=['GET'])
def connect_request():
    """
    Get method for camera to request a connection to the API server.
    Sends signal every 60 seconds to tell camera to get a fresh connection.
    Notifies camera once user has requested the EVENT_LOGS
    """
    start_time = time.time()

    while True:

        global CAM_RUNNING
        CAM_RUNNING = True

        # Re-establish a fresh connection after 60 seconds
        if (time.time() - start_time) >= 60:

            json_message = jsonify({"Reconnect": "Establish a new connection"})

            # Reset to False
            # (will get set back to True if another connection spins up)
            CAM_RUNNING = False

            return make_response(json_message, 350)

        # GET_REQUEST determines if a user has requested the camera EVENTS_LOG
        # Once requested, notify camera.
        global GET_REQUEST
        if GET_REQUEST:
            GET_REQUEST = False

            json_message = jsonify({"Accepted": "User requested EVENTS_LOG"})

            return make_response(json_message, 200)


@app.route('/logs', methods=['GET'])
def user_get_events():
    """
    Get method for a user to request EVENT_LOG from camera.
    Turns the global variable GET_REQUEST to True so that the
    Put method knows to accept the camera's connection request.
    Waits for RETURN_EVENTS to turn True and then returns the
    EVENTS list.
    """
    global GET_REQUEST
    GET_REQUEST = True

    while True:
        global RETURN_EVENTS
        if RETURN_EVENTS:
            RETURN_EVENTS = False

            return jsonify(EVENTS)


@app.route('/logs', methods=['PUT'])
def update_events():
    """
    Update the EVENTS list with json data from the client
    """
    global EVENTS
    EVENTS = request.json

    global RETURN_EVENTS
    RETURN_EVENTS = True

    return make_response(jsonify({'Success': 'Events log updated'}), 200)


@app.errorhandler(404)
def not_found(error):
    """
    Error handling if the user inputs the wrong URL.
    """
    json_message = jsonify({"Error": "Requested URL was not found. "
                            "Try 'curl -i http://172.18.0.2:5000/logs'"})

    return make_response(json_message, 404)


if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0')
