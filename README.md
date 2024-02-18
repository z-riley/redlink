# RedLink

RedLink is a Redis pub-sub wrapper which defines various message types.
Topics must be defined in a schema.

## Message Types

`EVENT`: Broadcast a message of an event happening.

`COMMAND`: Tell an instance to do something. Assumed successful - no response required.

`REQUEST`: Ask an instance to do something and expect data in return. May or may not happen.

`RESPONSE`: Respond to a request.

## Usage

See [example.py](example.py)
