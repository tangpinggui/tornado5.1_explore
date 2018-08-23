import tornado.web
import tornado.gen
from tornado.httpclient import HTTPClient, AsyncHTTPClient
from tornado import httpclient
from handlers.main.main_handler import AuthBaseHandler
from libs.main.main_libs import MainFileLib


class GetUrlHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        return self.render('grab.html')


class GrabPicturesHandler(AuthBaseHandler):
    @tornado.gen.coroutine
    def post(self):
        url = self.get_argument('url')
        if not url:
            return self.write('no url')

        http_client = AsyncHTTPClient()
        try:
            response = yield http_client.fetch(url, request_timeout=60) # 设置超时时间
            picture = MainFileLib('static', 'xxx.jpg')
            picture.save_file(content=response.body)

            picture.save_thumbs_file(content=response.body)
            post = picture.upload_file_and_thumbs_file(self.current_user)
            self.redirect('/post/%s' % post.id)
        except AttributeError:
            self.redirect('/grab')
