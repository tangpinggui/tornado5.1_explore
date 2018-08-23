import tornado.web
import uuid
from pycket.session import SessionMixin

from libs.main import main_libs
from models.db.db_config import dbSession
from models.auth.model import Posts, User
from models.db.conn import conn


class AuthBaseHandler(tornado.web.RequestHandler, SessionMixin):
    ''' 拥有数据库session的base类 '''
    def initialize(self):
        self.db = dbSession
        self.conn = conn

    def get_current_user(self):
        return self.session.get('cookie_name')  # 也可以查询user对象返回，感觉会更好


class MainHandler(AuthBaseHandler):
    """ 首页 """
    @tornado.web.authenticated
    def get(self):
        if self.current_user:
            user_posts = User.get_current_user_post(self.current_user)
            self.render('index.html', posts=user_posts)
        else:
            self.redirect('/login')


class ExploreHandler(AuthBaseHandler):
    """ 发现页 """
    @tornado.web.authenticated
    def get(self):
        posts = Posts.get_all()
        self.render('explore.html', posts=posts)


class ALoneHandler(AuthBaseHandler):
    """ 单独页 """
    @tornado.web.authenticated
    def get(self, id):
        post = Posts.by_id(id)
        self.render('alone.html', post=post)


class UploadHandler(AuthBaseHandler):
    """ 接收图片并储存,再储存一张缩略图 """
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        self.render('upload.html')

    def post(self, *args, **kwargs):
        files = self.request.files.get('files')  # [{'filename': x, 'body': x..., 'content_type': 'image/jpeg'},]
        if files:
            for file in files:
                picture = main_libs.MainFileLib('static', file['filename'])
                picture.save_file(file['body'])
                picture.save_thumbs_file(file['body'])
                if self.current_user:
                    picture.upload_file_and_thumbs_file(self.current_user)
                    return self.redirect('/upload')
                else:
                    return self.write('to db error')
        else:
            self.write('no choice any files')