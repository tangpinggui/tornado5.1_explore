import tornado.web
from handlers.main.main_handler import AuthBaseHandler
from sqlalchemy.sql import exists

from libs.auth import auth_lib


class RegisterHandler(AuthBaseHandler):
    def get(self):
        self.render('register.html')

    def post(self, *args, **kwargs):
        username = self.get_argument('username', '')
        password1 = self.get_argument('password1', '')
        password2 = self.get_argument('password2', '')
        result = auth_lib.register_user_data(self, username, password1, password2)
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
        self.write('logout success')