# virtual_camera_server
Web service containing a virtual camera which communicates with a server. Everything is wrapped up in a docker-compose session.

The virtual camera "records" events in an event log. The camera doesn't have any open ports or server for security purposes. It communicates with an API server by making an outgoing request to the server which is kept open until a user wants to fetch the event log data from the camera.

The server fetches this data when prompted by a user via a curl request which returns the events log as a JSON array with timestamps and event descriptions.

The camera reopens a new request to the API server every minute to ensure a fresh connection.

------------------

# Command to start system:
docker-compose up --build --force-recreate

# curl request to test endpoint:
curl -i http://0.0.0.0:5000/logs
