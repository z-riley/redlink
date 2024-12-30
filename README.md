# RedLink

RedLink can be used to send structured messages over Redis pub-sub.

The structure of the messages can be defined by the user in a JSON schema. If no schema is supplied, the default [schema.json](schema.json) is used.

## Message Types

`EVENT`: Broadcast a message of an event happening.

`COMMAND`: Tell an instance to do something. Assumed successful - no response required.

`REQUEST`: Ask an instance to do something and expect data in return. May or may not happen.

`RESPONSE`: Respond to a request.

## Usage

See [example.py](example.py)
