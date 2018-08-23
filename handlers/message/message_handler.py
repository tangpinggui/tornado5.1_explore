# coding=utf-8
from datetime import datetime
import logging
import tornado.web
import tornado.escape
import tornado.websocket
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient
from pycket.session import SessionMixin

from models.db.db_config import dbSession
from models.db.conn import conn
from models.auth.model import User
from handlers.main.main_handler import AuthBaseHandler


class WebBaseHandler(tornado.websocket.WebSocketHandler, SessionMixin):
    def initialize(self):
        self.conn = conn
        self.db = dbSession

    def get_current_user(self):
        current_name = self.session.get('cookie_name')
        user = None
        if current_name:
            user = User.by_name(current_name)
        return user if user else None

    def on_finish(self):
        self.db.close()


class MessageHandler(AuthBaseHandler):
    ''' 发表说说页面 '''
    @tornado.web.authenticated
    def get(self):
        """
        :return: 获取缓存信息，最近的五条
        """
        cache = self.conn.lrange('message:list', -5, -1)
        # print cache  ['{"datetime": "2018-04-20 17-46-58", "useravatar": "23033569-73bd-4872-be6f-8126dd62ecf1.jpeg",}]
        cache.reverse() # 消息顺序反转
        cache_list = []
        for ca in cache: # ca = '{"a": "1"} json
            massage_dict = tornado.escape.json_decode(ca) # 转为dict {"a": "1"}
            cache_list.append(massage_dict)
        kw = {
            'cache': cache_list,
        }
        self.render("message_chat.html", **kw)


class WebSocketHandler(WebBaseHandler, SessionMixin):
    ''' websocket '''
    users = {} # {u'liubei': <handlers.message.message_handler.WebSocketHandler object at 0xb620b34c>,
               #  u'rock': <handlers.message.message_handler.WebSocketHandler object at 0xb61794ec>}

    def get_current_user(self):
        current_name = self.session.get('cookie_name')
        user = None
        if current_name:
            user = User.by_name(current_name)
        return user if user else None

    def save_and_send_everone(self, msg):
        message = tornado.escape.json_encode(msg)  # 转成json

        self.conn.rpush('message:list', message)  # 存储消息为了显示历史消息
        for f, v in WebSocketHandler.users.items():
            v.write_message(message)

    def open(self):
        '''
        有用户进来后，存储该用户 {usernaem: self} self是每个登录用户的实例化类
        （用该实例化对象发送是那个消息）
        '''
        WebSocketHandler.users[self.current_user.name] = self
        for f, v in WebSocketHandler.users.items():
            try:
                v.write_message({"come": "%s进入了聊天室🌹" % self.current_user.name, "many": len(WebSocketHandler.users)})
            except Exception as e:
                print(e)

    def on_message(self, message):
        # print(message,'???') # {"content_html":"聊天框输入的内容"} json
        # {"content_html":"afaf<img src=\"/static/images/face/nm_thumb.gif\" title=\"[怒骂]\">"}
        msg = tornado.escape.json_decode(message)  # 解码 json字符串 --> 字符串
        msg_content = msg['content_html']
        if msg_content == "jiamide1":  # 心跳机制发送的数字{"content_html":"1"}
            return self.write_message({'heart': 'jiamide2'})

        msg.update({
            "name": self.current_user.name,
            "datetime": datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        })
        if msg_content.startswith('https://'):
            url = 'http://localhost:8000/grab_picture?url={}&user={}&from=room'.format(msg_content, self.current_user.name)
            tishi = "系统正在处理您的url:   <a href={}>{}</a>".format(msg['content_html'], msg['content_html'])
            msg.update({'content_html': tishi})
            print(url)
            # start async to garb url
            aysnc_client = AsyncHTTPClient()
            # on_message本身不在ioloop循环中，需要通过IOLoop调用协程
            try:
                IOLoop.current().spawn_callback(aysnc_client.fetch, url, request_timeout=60)  # h后台运行，不等待结果,
            except:
                msg.update({'content_html': '请求超时 '})
            self.write_message(msg)

        else:

            # self.write_message(msg) # 就算不转成json，write_message也能自己编码

            # WebSocketHandler.users['liubei'].write_message(message) # 这是将不管谁的message只发给用户liubei
            logging.info('聊天室人数：%s' % len(WebSocketHandler.users))
            self.save_and_send_everone(msg=msg)

    def on_close(self):
        WebSocketHandler.users.pop(self.current_user.name)
        for f, v in WebSocketHandler.users.items():
            v.write_message({'reduce': 1})
        logging.info('聊天室人数：%s' % len(WebSocketHandler.users))
