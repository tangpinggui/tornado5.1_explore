# coding=utf-8
from datetime import datetime

import logging
import tornado.web
import tornado.escape
# from libs.flash.flash_lib import flash

from handlers.ws.ws_handler import WsBaseHandler as WebBaseHandler
from handlers.main.main_handler import AuthBaseHandler as BaseHandler
# from libs.message import message_lib


class SendMessageHandler(WebBaseHandler):
    ''' 发送消息页面 '''
    def get(self):
        self.conn.delete('massage:%s' % self.current_user.name) # 到这个页面删除拥护邮件记录
        kw = {
            # 'roles': Role.all(),
            'roles': [],
            'user_msg': self.get_redis_json_to_dict('user'),
            'role_msg': self.get_redis_json_to_dict('role'),
            'system_msg': self.get_redis_json_to_dict('system'),
        }
        self.render('message/message_send_message.html', **kw)

    def get_redis_json_to_dict(self, target):
        msgs = self.conn.lrange('message:%s' %target, -5, -1)
        msgs.reverse()
        dict_list = []
        for msg in msgs:
            msg_dict = tornado.escape.json_decode(msg)
            dict_list.append(msg_dict)
        return dict_list

    def post(self):
        content = self.get_argument('content', '')
        send_type = self.get_argument('send_type', '')
        user = self.get_argument('user', '')
        roleid = self.get_argument('roleid', '')
        if send_type == 'user':
            WebSocketHandler.send_user_message(self, content, send_type, user)
        if send_type == 'role':
            WebSocketHandler.send_role_message(self, content, send_type, roleid)
        if send_type == 'system':
            WebSocketHandler.send_system_message(self, content, send_type)
        self.redirect('/message/send_message')


class MessageHandler(BaseHandler):
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


class WebSocketHandler(WebBaseHandler):
    ''' websocket '''
    users = {} # {u'liubei': <handlers.message.message_handler.WebSocketHandler object at 0xb620b34c>,
               #  u'rock': <handlers.message.message_handler.WebSocketHandler object at 0xb61794ec>}

    # ------------------提高部分 开始------------------
    @classmethod
    def send_system_message(cls, self, content, send_type):
        """
        :param self: 继承过websocket的base类的实例化对象，主要是self初始化了操作redis，mysql以及user对象的属性
        :param content: 储存进redis的list data
        :param send_type: 发送的类型（发给boss，ceo，员工...），由前端传过来
        :return: 系统消息，发送给每个人
        """
        target = 'system'
        redis_msg = cls.dict_to_json(self, content, send_type, target)
        self.conn.rpush('message:%s' % send_type, redis_msg)

        for f, v in WebSocketHandler.users.items():
            v.write_message(redis_msg)


    @classmethod
    def dict_to_json(cls, self, content, send_type, target):
        """
        :param self:  继承过websocket的base类的实例化对象，主要是self初始化了操作redis，mysql以及user对象的属性
        :param content: 储存进redis的list data
        :param send_type: 发送的类型（发给boss，ceo，员工...），由前端传过来
        :param target: 相当与用来区分缓存key的名字，比如 key_name="cache_list:%s"%target1, ...取对应分类的历史数据
        :return:
        """
        msg = {
            "content": content,
            "send_type": send_type,
            "sender": self.current_user.name,
            "target": target,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return tornado.escape.json_encode(msg)

    @classmethod
    def send_role_message(cls, self, content, send_type, roleid):
        """
        :param self:
        :param content:
        :param send_type:
        :param roleid: 通过角色id，反查出属于该角色id的用户
        :return: 发送信息给 该角色的所用用户
        """
        role = Role.by_id(roleid)
        redis_msg = cls.dict_to_json(self, content, send_type, role.name)
        self.conn.rpush('message:%s' % send_type, redis_msg)
        role_users = role.users  # [zhangsan, lishi , wangwu]  [zhangsan, lishi]
        for user in role_users:
            if WebSocketHandler.users.get(user.name, None) is not None: # user.name ['rock':self]
                WebSocketHandler.users[user.name].write_message(redis_msg)
            else:
                # self.conn.lpush("ws:role_off_line",message)
                pass

    @classmethod
    def send_user_message(cls, self, content, send_type, user):
        """
        :param self:
        :param content:
        :param send_type:
        :param user: 发送的对象
        :return: 发送信息给改用户 user
        """
        redis_msg = cls.dict_to_json(self, content, send_type, user)

        self.conn.rpush('message:%s' % send_type, redis_msg)
        self.conn.rpush('message:%s' % user, redis_msg) # 为了显示未读消息条数

        if cls.users.get(user, None) is not None:
            cls.users[user].write_message(redis_msg)
        else:
            # self.conn.lpush("ws:user_off_line",message)
            pass

    # ------------------提高部分 结束------------------

    def open(self):
        '''
        有用户进来后，存储该用户 {usernaem: self} self是每个登录用户的实例化类
        （用该实例化对象发送是那个消息）
        '''
        WebSocketHandler.users[self.current_user.name] = self
        pass

    def on_message(self, message):
        print(message,'???') # {"content_html":"聊天框输入的内容"} json
        # {"content_html":"afaf<img src=\"/static/images/face/nm_thumb.gif\" title=\"[怒骂]\">"}
        msg = tornado.escape.json_decode(message)  # 解码 json字符串 --> 字符串
        if msg['content_html'] == "jiamide1":  # 心跳机制发送的数字{"content_html":"1"}
            return self.write_message('2')
        else:
            print('coming..')
            msg.update({
                "name": self.current_user.name,
                "datetime": datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            })

            message = tornado.escape.json_encode(msg) # 转成json

            self.conn.rpush('message:list', message)  # 存储消息为了显示历史消息

            # self.write_message(msg) # 就算不转成json，write_message也能自己编码

            # WebSocketHandler.users['liubei'].write_message(message) # 这是将不管谁的message只发给用户liubei
            logging.info('聊天室人数：%s' % len(WebSocketHandler.users))
            for f, v in WebSocketHandler.users.items():
                v.write_message(message)

    def on_close(self):
        pass