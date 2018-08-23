from datetime import datetime

import tornado.web
import tornado.gen
import tornado.escape
from tornado.httpclient import HTTPClient, AsyncHTTPClient
from tornado import httpclient
from handlers.main.main_handler import AuthBaseHandler
from libs.main.main_libs import MainFileLib
from handlers.message.message_handler import WebSocketHandler


class GetUrlHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        message = "开始抓取图片"
        return self.render('grab.html', message=message)


class GrabPicturesHandler(AuthBaseHandler):
    @tornado.gen.coroutine
    def get(self):
        url = self.get_argument('url','')
        user = self.get_argument('user','')
        is_room = self.get_argument('from','') == 'room'
        if not url:
            return self.write('no url')

        http_client = AsyncHTTPClient()
        try:
            response = yield http_client.fetch(url, request_timeout=60)  # 设置超时时间
        except:
            timeout = {
                'name': user,
                "datetime": datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
                'content_html': "处理超时"
            }
            return WebSocketHandler.users[user].write_message(timeout)

        picture = MainFileLib('static', 'xxx.jpg')
        picture.save_file(content=response.body)
        picture.save_thumbs_file(content=response.body)
        if user:
            post = picture.upload_file_and_thumbs_file(user)
        else:
            post = picture.upload_file_and_thumbs_file(self.current_user)
        print(post.thumbs_url, '............')
        if user and is_room:
            static_thumbnail_url = "http://192.168.0.121:8000/static/" + post.thumbs_url
            result = '处理结果url:<a href={}><img src={} alt=""></a>'.format(static_thumbnail_url, static_thumbnail_url)
            print(result, 'new')
            result_msg = {
                'name': user,
                "datetime": datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
                'content_html': result
            }
            WebSocketHandler.save_and_send_everone(self, msg=result_msg)
        else:
            self.redirect('/post/%s' % post.id)


class TimeOutHandler(AuthBaseHandler):
    def get(self):
        message = "请求超时"
        self.render('timeout.html', message=message)
