"""gateway.py
Gateway for services to use to send and receive RedLink messages
"""
import os
import redis
import json
import jsonschema
from threading import Thread
from loguru import logger
from typing import Callable


class MessageType():
    EVENT = "EVENT"
    COMMAND = "COMMAND"
    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"


class RedLinkCore():
    """Core RedLink functionality"""

    def __init__(self, schema_path, source):
        self.SCHEMA_PATH = schema_path
        self.source = source
        redis_host = os.getenv("REDIS_HOST", default="localhost")
        redis_port = os.getenv("REDIS_PORT", default="6379")
        self._redis_client = redis.StrictRedis(host=redis_host, port=redis_port)
        self._pubsub = self._redis_client.pubsub()
        self._callback_table = {}

    def subscribe(self, topic, callback: Callable):
        """Subscribe to a topic"""

        self.register_callback(topic, callback)

        if self._topic_is_valid(topic):
            self._pubsub.subscribe(topic)
        else:
            logger.error(f"Invalid topic: \"{topic}\". See \"{self.SCHEMA_PATH}\" for valid topics")

    def publish(self, message_type, topic, payload):
        """Publish a RedLink message"""

        message = {
            "messageType": message_type,
            "topic": topic,
            "source": self.source,
            "payload": payload,
            }
        
        if self._message_is_valid(message):
            self._redis_client.publish(channel=message["topic"], message=json.dumps(message))
        else:
            logger.error("Message not sent")

    def register_callback(self, topic, callback: Callable):
        """Register a callback function that triggers when message with a specified topic is received"""
        if self._topic_is_valid(topic):
            self._callback_table[topic] = callback
        else:
            logger.warning(f"Failed to register callback. Invalid topic: \"{topic}\"")

    def begin_listening(self):
        """Spawn listener thread"""
        listener_thread = Thread(target=self._listen, daemon=True)
        listener_thread.start()

    def _listen(self):
        """Listen to subscribed topics for incoming messages"""
        for message in self._pubsub.listen(): # infinite loop
            if message["type"] == "message":
                self._on_receive(message)

    def _on_receive(self, message):
        """Handles received messages and routes it to relevant callback"""
        msg_data = json.loads(message["data"])
        topic = msg_data["topic"]
        if topic in self._callback_table:
            # Run the callback registered to the topic
            self._callback_table[topic](json.loads(message["data"]))
        else:
            logger.warning(f"Topic \"{topic}\" has no registered callback")
        
    def _message_is_valid(self, message):
        """Check if message is valid according to the schema"""
        with open(self.SCHEMA_PATH, "r") as file:
            schema = json.load(file)
        try:
            jsonschema.validate(message, schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            logger.error(f"Validation error: {e.message}")
            return False
        
    def _topic_is_valid(self, topic):
        """Check if topic is valid according to schema"""
        with open(self.SCHEMA_PATH, "r") as file:
            schema = json.load(file)
        valid_topics = schema["properties"]["topic"]["enum"]
 
        if topic in valid_topics:
            return True
        else:
            return False


class RedLinkGateway(RedLinkCore):
    """Wrapper methods for message types"""
    
    PATH = os.path.join(os.path.dirname(__file__), "schema.json")

    def __init__(self, source, schema_path=PATH):
        super().__init__(schema_path, source)

    def event(self, topic, payload):
        self.publish("EVENT", topic, payload)
    
    def command(self, topic, payload):
        self.publish("COMMAND", topic, payload)

    def request(self, topic, payload):
        self.publish("REQUEST", topic, payload)

    def respond(self, topic, payload):
        self.publish("RESPONSE", topic, payload)

