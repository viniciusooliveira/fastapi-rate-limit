import re
import threading
import time

from redis import Redis


class RedisSubscribeWorker:
    def __init__(self,
                 subscription_key: str,
                 host: str = "localhost",
                 port: int = 6379,
                 password: str = None):

        self._con = Redis(host=host, port=port, password=password)
        self._pubsub = self._con.pubsub()
        self._pubsub.psubscribe(f"__keyspace@0__:{subscription_key}:*",)

        self.sub_key = subscription_key

        self._stopping = False
        self._thread = None
        self._values: dict = {}

    def start(self):
        self._thread = threading.Thread(name="RedisSubWorker", target=self.run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stopping = True
        self._thread.stop()

    def run(self):
        while not self._stopping:
            message = self._pubsub.get_message()
            if message is None:
                time.sleep(0.01)
            elif message["type"] == "pmessage":

                print(message)
                key = re.sub(r"^.*?"+self.sub_key+r"\:", "", message["channel"].decode())
                print(key)

                message_type = message["data"].decode()

                if (message_type == 'expired'
                        or message_type == 'del'):
                    self._on_delete(key)

                if (message_type == 'set'
                        or message_type == 'incrby'
                        or message_type == 'incrbyfloat'):
                    self._on_change(key)

                # self._values[key] = self._con.get(f"{self.sub_key}:{key}")
                print(self._values)
                # self._con.incr(f"{self.sub_key}:{key}", 1)

    def _on_change(self, key):
        self._values[key] = self._con.get(f"{self.sub_key}:{key}")

    def _on_delete(self, key):
        try:
            del self._values[key]
        except KeyError:
            pass

    def incr(self, key, expiration: int = 60):
        return self.incrby(key, 1, expiration)

    def incrby(self, key, value: int, expiration: int = 60):
        return self._con.eval("""local current
            current = redis.call("incrby",KEYS[1], ARGV[1])
            if current == 1 then
                redis.call("expire",KEYS[1], ARGV[2])
            end
            return current""", 1, f"{self.sub_key}:{key}", value, expiration)

    def incrbyfloat(self, key, value: float, expiration: int = 60):
        return self._con.eval("""local current
            current = redis.call("incrbyfloat",KEYS[1], ARGV[1])
            if current == 1 then
                redis.call("expire",KEYS[1], ARGV[2])
            end
            return current""", 1, f"{self.sub_key}:{key}", value, expiration)

    def get(self, key):
        value = self._values.get(key)
        if value is not None:
            return value
        value = self._con.get(f"{self.sub_key}:{key}")
        if value is not None:
            self._values[key] = value.decode()
            return self._values[key]
        return None

    def getint(self, key):
        return int(self.get(key) or 0)

    def getfloat(self, key):
        return float(self.get(key) or 0)

    def list_stored_values(self):
        return self._values

