import random
from paho.mqtt import client as mqtt_client


class ETLPipeline:
    def __init__(self, topics: list):
        self.topics = topics
        self.subscriber_list = []
        self.broker_adress = None
        self.port = None
        self.init_db()

    def transform_data(self):
        pass

    def init_db(self):
        pass

    def load_into_db(self):
        pass


class mqtt_pipeline(ETLPipeline):
    """ETL pipeline using mqtt protocoll."""

    def __init__(self, topics):
        super().__init__(topics)

    def init_subscriber(self):
        """Define a general paho mqtt subscriber."""
        
        client_id = f"mqtt_subscriber-{random.randint(0, 1000)}"

        # callback for subscription
        def on_subscribe(client, userdata, mid, reason_code_list, properties):
            if reason_code_list[0].is_failure:
                print(f"Broker rejected you subscription: {reason_code_list[0]}")
            else:
                print(f"Broker granted the following QoS: {reason_code_list[0].value}")

        # callback for unsubscription
        def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
            if len(reason_code_list) == 0 or not reason_code_list[0].is_failure:
                print(
                    "unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)"
                )
            else:
                print(f"Broker replied with failure: {reason_code_list[0]}")
            client.disconnect()

        # callback for messages
        def on_message(client, userdata, message):
            userdata.append(message.payload)
            # We only want to process 10 messages
            if len(userdata) >= 10:
                client.unsubscribe("$SYS/#")

        # callback function when client receives a CONNACK response from the server
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code.is_failure:
                print(
                    f"Failed to connect: {reason_code}. loop_forever() will retry connection"
                )
            else:
                pass
                # client.subscribe("$SYS/#")

        # callback for when client receives a disconnect response from server
        def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
            if reason_code == 0:
                print("Disconnected from MQTT Broker")
            else:
                print("Failed to disconnect, return code %d/n", reason_code)

        subscriber = mqtt_client.Client(client_id=subscriber_id, mqtt_client.CallbackAPIVersion.VERSION2)
        subscriber.on_connect = on_connect
        subscriber.on_message = on_message
        subscriber.on_subscribe = on_subscribe
        subscriber.on_unsubscribe = on_unsubscribe
        subscriber.on_disconnect = on_disconnect
        
        return subscriber

    def init_broker(self, adress: str, port: int):
        """Set mqtt broker."""

        self.broker_adress = adress
        self.broker_port = port

    def subscribe_to_topic(self, topic: str):
        """Connect mqtt client to a topic and start to listen."""

        self.subscriber.user_data_set([])
        self.subscriber.connect(self.broker_adress, self.port)
        self.subscriber.subscribe(topic)
        
    def start_to_listen(self):
        
        for topic in self.topics:
            subscriber = self.init_subscriber()
            
