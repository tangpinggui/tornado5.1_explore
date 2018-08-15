import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

from handlers.main import main_handler
from handlers.auth import auth_handler


define('port', default=8000, type=int, help='Listening port')
##

class AppConfig(tornado.web.Application):
    """ 继承了Application重写init，再将重写的参数通过super传给Application """
    def __init__(self):
        handlers = [
            (r'/', main_handler.MainHandler),
            (r'/post/(?P<id>[0-9]{1,})', main_handler.ALoneHandler),
            (r'/explore', main_handler.ExploreHandler),
            (r'/upload', main_handler.UploadHandler),
            (r'/login', auth_handler.LoginHandler),
            (r'/logout', auth_handler.LogoutHandler),
            (r'/register', auth_handler.RegisterHandler),
            (r'/profile', auth_handler.ProfileHandler),
        ]
        settings = dict(
            debug=True,
            template_path='templates',
            static_path='static',
            login_url='/login',
            cookie_secret='fagawg',
            pycket={
                'engine': 'redis',
                'storage': {
                    'host': 'localhost',
                    'port': 6379,
                    'db_sessions': 2,
                    # 'password': '',
                    'db_notifications': 11,
                    'max_connections': 2 ** 31,
                },
                'cookies': {
                    'expires_days': 30,
                    'max_age': 5000
                }
            },
        )
        super(AppConfig, self).__init__(handlers=handlers, **settings)


application = AppConfig()
### or
'''
handlers = [
    (r'/', main_handler.MainHandler),
]
settings = dict(
    debug=True,
    template_path='templates',
    static_path='static'
)
application=tornado.web.Application(handlers=handlers, **settings)
'''

if __name__ == '__main__':
    options.parse_command_line()
    application.listen(options.port)
    print('Sever start on port {}...'.format(options.port))
    tornado.ioloop.IOLoop.current().start()