import tornado.web
from handlers.main.main_handler import AuthBaseHandler


class LoginHandler(AuthBaseHandler):
    def get(self):
        username = self.get_argument('username', 'tpg')
        passwd = self.get_argument('password', 'tttt')
        if username and passwd:
            self.session.set('cookie_name', username)
            self.write('success login')


class LogoutHandler(AuthBaseHandler):
    def get(self):
        self.session.delete('cookie_name')
        self.write('logout success')