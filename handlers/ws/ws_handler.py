import logging
import redis
import tornado.escape
import tornado.web
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
        self.conn = rds  # redis

    def get_current_user(self):
        username = self.session.get('cookie_name')
        user = None
        if username:
            user = User.by_name(name=username)
        return user if user else None


class SendMessageHandler(WsBaseHandler):
    @tornado.web.authenticated
    def get(self):
        cache = self.conn.lrange('message:list', -5, -1)
        cache.reverse()
        cache_list = []
        for ca in cache:
            message_dict = tornado.escape.json_decode(ca)
            cache_list.append(message_dict)
        kw = {
            'cache': cache_list
        }
        self.render('message.html', **kw)




class WebSocketHandler(WsBaseHandler):
    users = {}

    def get_compression_options(self):
        """ 非None的返回值，开启压缩 """
        return {}

    def open(self):
        print('-------'*10,'open')
        logging.info('start a connection with %s' % self)
        self.users[self.current_user.name] = self

    def on_message(self, message):
        print('-----'*10,message)
        msg = tornado.escape.json_decode(message)
        msg.update({
            'name': self.current_user.name,
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        message = tornado.escape.json_encode(msg)
        self.conn.rpush('message:list', message)
        for _, v in WebSocketHandler.users.items():
            v.write_message(message)

    def on_close(self):
        print('-------'*10,'close')
        logging.info("end connection")
        self.users.pop(self.current_user.name)