import logging
import redis
import tornado.escape
from datetime import datetime
from tornado.websocket import WebSocketHandler
from pycket.session import SessionMixin

from models.db.db_config import dbSession
from models.auth.model import User

rds = redis.Redis()


class WsBaseHandler(WebSocketHandler, SessionMixin):
    ''' websocket通信需要先创建websocket base类 '''

    def initialize(self):
        self.db = dbSession  # mysql
        self.rds = rds  # redis

    def get_current_user(self):
        username = self.session.get('cookie_name')
        user = None
        if username:
            user = User.by_name(name=username)
        return user if user else None


class SendMessageHandler(WsBaseHandler):
    def get(self):
        cache = self.rds.lrange('message:list', -5, -1)
        cache.reverse()
        self.render('message.html', messages='hellow word')


class WebSocketHandler(WsBaseHandler):
    message_users = {}

    def open(self):
        logging.info('start a connection with %s' % self)
        self.message_users[self.current_user.name] = self

    def on_message(self, message):
        print(message)
        msg = tornado.escape.json_decode(message)
        message.update({
            'name': self.current_user.name,
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        message = tornado.escape.json_encode(msg)
        self.rds.rpush('message:list', message)
        for k, v in message.items():
            v.write_message(message)

    def on_close(self):
        logging.info("end connection")
        self.message_users.pop(self.current_user.name)