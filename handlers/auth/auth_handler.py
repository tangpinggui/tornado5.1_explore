import json
import tornado.web
from handlers.main.main_handler import AuthBaseHandler
from sqlalchemy.sql import exists

from libs.auth import auth_lib
from models.auth.model import Posts, Like, User


class RegisterHandler(AuthBaseHandler):
    def get(self):
        self.render('register.html')

    def post(self, *args, **kwargs):
        username = self.get_argument('username', '')
        password1 = self.get_argument('password1', '')
        password2 = self.get_argument('password2', '')
        result = auth_lib.register_user_data(self, username, password1, password2)
        if result['status']:
            return self.redirect('/login')
        return self.write(result['message'])


class LoginHandler(AuthBaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument('username', '')
        passwd = self.get_argument('password', '')
        next = self.get_argument('next', '')
        result = auth_lib.login_auth(self, username, passwd)
        if result['status']:
            self.session.set('cookie_name', username)
            if not next:
                self.redirect('/')
            else:
                self.redirect(next)
        else:
            self.write(result['message'])


class LogoutHandler(AuthBaseHandler):
    def get(self):
        self.session.delete('cookie_name')
        self.redirect('/login')


class ProfileHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def get(self):
        username = self.get_argument('username', '')
        posts = Posts.self_uploads_img(username)
        user = User.by_name(name=username)

        lists = []
        for post in posts:
            num = Like.get_file_like_num(post.id)
            red = Like.red(user.id, post.id)
            lists.append({'post': post, 'num': num, 'red':red})  # file obj, dianzan num, 是否已点赞
        self.render('profile.html', lists=lists)


class ProfileLikeHandler(AuthBaseHandler):
    @tornado.web.authenticated
    def post(self):
        status = int(self.get_argument('status'))  # 0取消点赞: or 1点赞
        file_id = int(self.get_argument('file_id'))
        result = auth_lib.add_or_del_like(status, file_id, self.current_user)
        self.write(json.dumps(result))