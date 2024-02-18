"""example.py
Example script
"""
import json
import time
import redlink

class ExampleService():

    def __init__(self):
        self.gateway = redlink.RedLinkGateway(schema_path="schema.json", source="exampleService")

        # Subscribe to desired topics and set callbacks
        self.gateway.subscribe("interestingTopic1", self.my_cb)
        self.gateway.subscribe("interestingTopic2", self.my_cb)
        self.gateway.subscribe("status", self.status_cb)

        self.gateway.begin_listening()
    
    def my_cb(self, message):
        if message["messageType"] == redlink.MessageType.RESPONSE:
            response = json.loads(message["data"])["payload"]
            print(f"Received response: {response}")

    def status_cb(self, message):
        if message["messageType"] == redlink.MessageType.COMMAND:
            print(f"Received command: {message}")

    def request_status(self):
        self.gateway.request("status", "")

    def set_status(self, status):
        self.gateway.command("status", status)
            
    def run(self):
        while True:
            self.request_status()
            time.sleep(2)
            self.set_status("ACTIVE")
            time.sleep(2)


if __name__ == "__main__":
    example_service = ExampleService()
    example_service.run()
