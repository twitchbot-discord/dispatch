import json
import logging
import pika
import time

from os import getenv
from rethinkdb import RethinkDB
from threading import Thread
from . import rethink

r = RethinkDB()


class AmqpConsumerThread:
    def __init__(self):
        self.thread = None
        self.allowed_keys = {
            'level': 1,
            'channel': 'default',
            'source': 'default',
            'msg': None,
            'ts': 0,
            'data': {}
        }
        self.connection = self._open_conn()
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='dispatch.logs')
        logging.info('Connected to AMQP')

    def _open_conn(self):
        return pika.BlockingConnection(pika.ConnectionParameters(getenv('AMQP_ADDR')))

    def _callback(self, channel, method, properties, body):
        body = json.loads(body.decode())
        body = {**self.allowed_keys, **body}
        logging.info('Received message %s', body)

        if body.get('op') == 1:
            # Logging opcode

            if len(body.get('data', {}).keys()) > 64:
                # Ignore events with more than 64 data attributes
                return

            re = rethink.connect()
            if body.get('ts', 0) == 0:
                body['ts'] = r.epoch_time(body['ts'])
            else:
                body['ts'] = r.epoch_time(time.time())
            r.table('logs')\
                .insert({k: v for k, v in body.items() if k in self.allowed_keys.keys()})\
                .run(re, durability='soft', noreply=True)
            re.close()
            logging.info('Inserted row into db')

    def _main(self):
        self.channel.basic_consume(queue='dispatch.logs', auto_ack=True, on_message_callback=self._callback)
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logging.info('Exiting AMQP worker...')
        self.connection.close()

    def run(self):
        self.thread = Thread(target=self._main, daemon=True)
        self.thread.start()
