import rabbitpy
from threading import Thread

class RabbitManager(object):
    QUEUE_NAME = 'suggest'
    EXCHANGE_NAME = 'message'
    EXCHANGE_TYPE = 'topic'
    ROUTING_KEY = 'worker.message'
    HOST = 'localhost'
    PORT = 5672
    VHOST = '/'
    USER = 'guest'
    PASSWORD = 'guest'
    EXCHANGE_NAME = 'test_exchange'
    QUEUE_NAME = 'test_queue'

    def __init__(self):
        self._channel = None
        self._queue = None
        self._exchange = None
        self._connection = None
        self._connect()

    def _connect(self):
        self._connection = rabbitpy.Connection()
        self._channel = self._connection.channel()
        self._channel.enable_publisher_confirms()

        self._exchange = rabbitpy.Exchange(self._channel, self.EXCHANGE_NAME, self.EXCHANGE_TYPE)
        self._exchange.declare()

        self._queue = rabbitpy.Queue(self._channel, self.QUEUE_NAME)
        self._queue.declare()

        self._queue.bind(self._exchange, self.ROUTING_KEY)

    def send(self, msg):
        m = rabbitpy.Message(self._channel, msg)
        m.publish(self.EXCHANGE_NAME, self.ROUTING_KEY)

    def start_consuming(self):
        for message in self._queue.consume_messages():
            message.ack()

    def get(self):
        val = None
        try:
            val = self._queue.get(acknowledge=True)
            val.ack()
        except Exception:
            pass
        return val

global_rqueue = RabbitManager()


if __name__ == '__main__':
    rq = RabbitManager()

    def write():
        for i in range(100):
            rq.send(f'{i}')

    def listen():
        while True:
            rq.get()


    w = Thread(target=write)
    l = Thread(target=listen)

    w.start()
    l.start()

    w.join()
    l.join()

    print('finish')


