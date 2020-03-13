# Atlan Backend Internship Task

Build the docker image from here or pull `grapheo12/atlan-task` from dockerhub for testing. Exposed port is 8000.
Capabilities:

1. It can stop a running file upload in the middle.

2. It can stop a running row export in the middle.

Thereby covering the first two scenarios completely.
The third scenario can be easily extended from 2nd one
since the code that manages this delete procedure is generic.

Please use the Swagger UI on `/` route to test the APIs.
Two APIs are given: `/export` and `/upload`.
The flow has 3 parts for each API:
- Run a GET request to get a ticket.
- Run the actual POST request for export/upload of the data.
- To stop the running request, run a DELETE request and pass the ticket as a parameter.


Please run `run_tests.py` to get an interactive shell for testing.
It spawns a thread that runs a counter.
Counter can be paused(command: p), resumed(command: r) and terminated(command: t) at any time.
You can view the counter variable value by running command s (for show).

Please see tests/threadManagerTest.py for reference usage.
The context manager in action is defined in app/threadManager.py.
